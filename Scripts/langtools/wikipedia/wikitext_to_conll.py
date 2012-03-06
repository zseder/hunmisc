"""Parameters: the configuration file, the input file, the two outputs: the
pages and the templates files."""
# TODO: ' to separate token (currently it is not removed from the beginning of
#       words).

import re
import sys
from optparse import OptionParser
from itertools import chain
from langtools.utils.cascading_config import CascadingConfigParser

from langtools.utils.misc import remove_quot_and_wiki_crap_from_word
from langtools.utils.language_config import LanguageTools
from langtools.utils.file_utils import read_file_into_set

class WikipediaParser(object):
    """Base class for Wikipedia dump parsers."""
    page_separator = "%%#PAGE"
    ws_stripper = re.compile(r"\s*", re.UNICODE)

    # TODO: from ConfigParser
    def __init__(self, lt, config_file):
        """
        Uses the section <tt>self.lt.language</tt>-wikimedia.

        The following parameters are used:
        - whitelist: the file that contains the list of pages to retain.
        - blacklist: the file that contains the list of pages to discard.

        The two parameters whitelist and blacklist can be used to specify which
        pages will be kept and which pages will be thrown out. It is enough
        to specify only one of these two parameters, as the presence of either
        will trigger a filtering based on that list alone.

        @param lt the LanguageTools object.
        """
        self.lt = lt

        config_parser = CascadingConfigParser(config_file)
        config = dict(config_parser.items(self.lt.language.split('.')[0] + '-wikimedia'))

        self.whitelist = None
        self.blacklist = None
        whitelist_file = config.get('whitelist', None)
        blacklist_file = config.get('blacklist', None)
        if whitelist_file is not None:
            self.whitelist = read_file_into_set(whitelist_file, 'utf-8')
        if blacklist_file is not None:
            self.blacklist = read_file_into_set(blacklist_file, 'utf-8')

    def process_file(self, input_file):
        """Processes input_file, which is a file stream. Calls the
        parse_actual_page method per page."""
        actual_page = u""
        actual_title = u""
        skip = False
        for line in input_file:
            line = line.decode("utf-8")
            if line.startswith(WikipediaParser.page_separator):
                if actual_page != u"" and not skip:
                    self.parse_actual_page(actual_page, actual_title)
                actual_page = u""
                try:
                    actual_title = line.strip().split(" ", 1)[1]
                except IndexError:
                    sys.stderr.write("Page title contains only whitespace\n")
                    skip = True
                skip = self.filter_page(actual_title)
            else:
                actual_page += line

        if len(actual_page) > 0:
            self.parse_actual_page(actual_page, actual_title)

    def filter_page(self, title):
        """
        If True, the current page is SKIPPED.
        
        This default implementation skips all titles specified in the 
        blacklist file and retain all others, or retain all titles in
        the whitelist file and drop all others.
        """
        if self.whitelist is not None:
            return title not in self.whitelist
        elif self.blacklist is not None:
            return title in self.blacklist
        else:
            return False

    def parse_actual_page(self, actual_page, actual_title):
        from mwlib.uparser import parseString, simpleparse

        s = self.remove_xml_comments(actual_page)
        try:
            s = self.remove_open_close(s, "<math>", "</math>")
        except SyntaxException, se:
            s = self.remove_open_close_lame(s, "<math>", "</math>")
            sys.stderr.write(u"Problems with <math>: {0}\n".format(
                actual_title).encode("utf-8"))
 
        templates = self.process_templates(actual_title, s)

        try:
            s = self.remove_open_close(s, "{{", "}}")
        except SyntaxException:
            s = self.remove_open_close_lame(s, "{{", "}}")
            sys.stderr.write(u"Problems with braces: {0}\n".format(
                    actual_title).encode("utf-8"))
        try:
            #r=simpleparse(raw=s)
            #quit()
            r=parseString(raw=s, title=actual_title, lang=self.lt.language)
        except AssertionError:
            sys.stderr.write(u"AssertionError problem: {0}\n".format(
                    actual_title).encode("utf-8"))
            return
        except ImportError, e:
            sys.stderr.write(u"ImportError problem({0}): {1}\n".format(
                             e, actual_title).encode("utf-8"))
            return
        except AttributeError, e:
            excepted_error_message = "'ImageMap' object has no attribute 'imagelink'"
            if str(e).strip() == excepted_error_message:
                sys.stderr.write(u"imagemap/imagelink error: {0}\n".format(
                                 actual_title).encode("utf-8"))
                return
            else:
                raise e

        try:
            nh = NodeHandler()
            nh.handle(r)
            tokens = nh.tokens
        except RuntimeError, rte:
            print rte
            s = "maximum recursion depth exceeded"
            if str(rte).find(s) >= 0:
                sys.stderr.write(u"Maximum depth recursion at site: {0}\n".format(
                                 actual_title).encode("utf-8"))
                return
        tokens_to_process = self.tokens_from_title(actual_title)
        tokens_to_process += self.tokenize_all(tokens)
        self.process_tokens(actual_title, tokens_to_process, templates)

    def process_tokens(self, actual_title, tokens, templates):
        """
        Processes the tokens. Called after parse_actual_page splits the
        content of the page into tokens. Subclasses must override this method
        to process the tokens. This default implementation is a no-op.

        The first entry in @p tokens is the title; the body starts at index 1.
        @param actual_title the title of the page being processed.
        @param tokens the tokens.
        @param templates the templates found on the page.
        """
        pass

    def process_templates(self, actual_title, s):
        """
        Processes the templates found on the page.
        @param actual title the title of the page.
        @param s the page text.
        """
        pass

    def tokens_from_title(self, actual_title):
        """Tokenizes the title in the same way as the page text."""
        title_tokens = []
        for token in self.lt.word_tokenize(actual_title):
            title_tokens.append([token, "text", "0"])
        return [title_tokens]

    def remove_xml_comments(self, text):
        """Removes xml-style comments, I guess."""
        start = text.find("<!--")
        end = text.find("-->")
        #sys.stderr.write("%d %d\n" % (start, end))
        position = start
        while start >= 0 and end >= 0:
            if end < start:
                position = end + 1
            else:
                text = text[0:start] + text[end+3:]
            start = text.find("<!--", position)
            end = text.find("-->", position)
            #sys.stderr.write("%d %d\n" % (start, end))
        return text

    def remove_open_close(self, text, openstr, closestr):
        """@todo: docstring"""
        done = []
        depth = 0
        position = 0
        start = None
        while True:
            open = text.lower().find(openstr, position)
            close = text.lower().find(closestr, position)
            if depth == 0:
                if open < 0:
                    done.append(text[start:])
                    break
                else:
                    done.append(text[start:open])
                    start = open
                    depth += 1
                    position = open + len(openstr)
            else:
                if open > -1:
                    if close > -1:
                        if open < close:
                            depth += 1
                            position = open + len(openstr)
                        else:
                            depth -= 1
                            position = close + len(closestr)
                    else:
                        raise SyntaxException("Open without closing")
                else:
                    if close > -1:
                        depth -= 1
                        position = close + len(closestr)
                    else:
                        raise SyntaxException("No more braces in depth %d" % depth)
                if depth == 0:
                    start = position
        return " ".join(done)

    def remove_open_close_lame(self, text, openstr, closestr):
        """@todo: docstring"""
        while True:
            open = text.find(openstr)
            close = text.find(closestr, open)
            if open > -1 and close > -1:
                text = text[:open] + text[close + len(closestr):]        
            else:
                break
        return text

    def tokenize_part(self, tokens):
        """Here be dragons."""
        def __search_for_right_index(old_index, index_inside_old_token):
            good = False
            while not good:
                my_token = tokens[old_index][0][index_inside_old_token:]
                index_inside_old_token += len(WikipediaParser.ws_stripper.match(my_token).group(0))
                if index_inside_old_token == len(tokens[old_index][0]):
                    old_index += 1
                    index_inside_old_token = 0
                else:
                    good = True
            
            return old_index, index_inside_old_token
        
        part_string = "".join((t[0] for t in tokens))
        #print tokens
        #print part_string.encode("utf-8")
        text = self.lt.tokenize(part_string)
        #print [s for s in text]
        new_tokens = []
        old_index = 0
        index_inside_old_token = 0
        inside_link = False
        for sen in text:
            actual_sentence = []
            sen2 = []
            for tok in sen:
                tok = tok.strip()
                tps = tok.split()
                if len(tps) > 0:
                    for tp in tps:
                        sen2.append(tp)
#                if tok != ". . .":
#                    sen2.append(tok)
                else:
                    sen2.append(tok)
#                    sen2 += [".", ".", "."]
            sen = sen2
            
            for tok in sen:
                done = False
                added = False
                index_inside_new_token = 0
                while not done:
                    previous_old_index = old_index
                    old_index, index_inside_old_token = __search_for_right_index(old_index, index_inside_old_token)
                    if previous_old_index != old_index:
                        inside_link = False
                    
                    if not inside_link:
                        new_link_tag = tokens[old_index][1]
                    
                    if not added:
                        actual_sentence.append([tok, new_link_tag, tokens[old_index][2]])
                        added = True
                    
                    # new token is at the beginning of the actual old token
                    if tokens[old_index][0][index_inside_old_token:index_inside_old_token+(len(tok) - index_inside_new_token)] == tok[index_inside_new_token:]:
                        done = True
                        index_inside_old_token += len(tok) - index_inside_new_token
                        if len(tokens[old_index][0]) >= index_inside_old_token:
                            if tokens[old_index][1] == "B-link":
                                new_link_tag = "I-link"
                                inside_link = True
                        
                    # new token is longer than the rest of the actual old token
                    # example: [[Brazil]]ian
                    elif ( len(tok[index_inside_new_token:]) >= len(tokens[old_index][0][index_inside_old_token:]) and
                           ( tok[index_inside_new_token:index_inside_new_token + len(tokens[old_index][0][index_inside_old_token:])]
                             == tokens[old_index][0][index_inside_old_token:]) ):
                        index_inside_new_token += len(tokens[old_index][0][index_inside_old_token:])
                        old_index += 1
                        inside_link = False
                        index_inside_old_token = 0
                        if index_inside_new_token == len(tok) + 1:
                            done = True
                        
                        if not done and tokens[old_index][1] == "B-link":
                            new_link_tag = "I-link"
                            inside_link = True
                        
                    else:
                        print "TOKEN", tok.encode("utf-8")
                        print "TOKENS[old_index]", tokens[old_index][0].encode("utf-8")
                        print "TOKENS/2", tokens[old_index][0][index_inside_old_token:index_inside_old_token+(len(tok))].encode("utf-8")
                        print "New token is longer than old one!"
                        raise Exception("New token is longer than old one!")
            
            if len(actual_sentence) > 0:
                new_tokens.append(actual_sentence)
        return new_tokens

    def tokenize_all(self, tokens):
        """
        Tokenizes the page contents.
        @param tokens the WikiMedia text tokens
        @return sentence and word tokens
        """
        new_tokens = []
        for part in tokens:
            for dbl in self.tokenize_part(part):
                dbl = list(chain.from_iterable([[w] + l[1:] for w in remove_quot_and_wiki_crap_from_word(l[0])] for l in dbl))
                new_tokens.append(dbl)

        return new_tokens

    def __del__(self):
        #del self.lt
        pass

class WikitextToConll(WikipediaParser):
    def __init__(self, lt, config_file, pages_file, templates_file):
        """
        @param pages_file the output file stream to which the page text is written.
        @param templates_file templates are written to this file stream.
        """
        WikipediaParser.__init__(self, lt, config_file)
        self.pages_f     = pages_file
        self.templates_f = templates_file

    def process_tokens(self, actual_title, tokens, templates):
        """Tags and lemmatizes the tokens, then prints the result into the
        first output file."""
        # POS tag and lemmatize the data
        self.lt.pos_tag(tokens)
        self.lt.lemmatize(tokens)

        # Print the tagged tokens
        self.pages_f.write(u"{0}\t{1}\n".format(
                WikipediaParser.page_separator, actual_title).encode("utf-8"))

        self.pages_f.write(u"%%#Field\tTitle\n")
        self.print_tokens([tokens[0]])

        # TODO: redirect.
        # elif starter and l.startswith("REDIRECT"):
        #   print "%%#Redirect"
        self.pages_f.write(u"%%#Templates\t{0}\n".format(
                u",".join((t.strip().replace("\n", "") for t in templates))).encode("utf-8"))
        self.pages_f.write(u"%%#Field\tBody\n")
        self.print_tokens(tokens[1:])

    def print_tokens(self, tokens):
        """Prints @p tokens to the page content file."""
        for sen in tokens:
            for t in sen:
                try:
                    self.pages_f.write(u"\t".join(t).encode("utf-8") + "\n")
                except UnicodeError, ue:
                    print "Trying to print: "
                    for w in t:
                        if isinstance(w, unicode):
                            print w.encode('utf-8')
                        else:
                            print w
                    raise ue
            self.pages_f.write("\n")

    def process_templates(self, actual_title, s):
        """Prints the templates into the second output file."""
        from mwlib.expander import get_templates

        self.templates_f.write(u"{0} {1}\n".format(
                WikipediaParser.page_separator, actual_title).encode("utf-8"))
        if not WikitextToConll.write_templates_into_f(s, self.templates_f):
            sys.stderr.write(u"Problems with templates and mwparser: {0}\n".format(
                             actual_title).encode("utf-8"))
        return get_templates(s)

    @staticmethod
    def write_templates_into_f(raw, f):
        """Extracts the templates from the raw text and writes them to the file @p f."""
        from mwlib.templ.misc import DictDB
        from mwlib.expander import get_template_args
        from mwlib.templ.evaluate import Expander
        from mwlib.templ.parser import parse
        from mwlib.templ.nodes import Template
        
        e=Expander('', wikidb=DictDB())  
        todo = [parse(raw, replace_tags=e.replace_tags)]
        result = True
        while todo:
            n = todo.pop()
            if isinstance(n, basestring):
                continue

            if isinstance(n, Template) and isinstance(n[0], basestring):
                d = get_template_args(n, e)
                f.write(u"Template\t{0}\n".format(unicode(n[0]).strip().replace("\n", "")).encode("utf-8"))
                for i in range(len(d)):
                    try:
                        f.write(unicode(d[i]).encode("utf-8") + "\n")
                    except TypeError:
                        result = False
                    except AttributeError:
                        # handling some mwlib bug. it raises this exception somehow
                        result = False
                f.write("\n")
            todo.extend(n)
        return result

    def close(self):
        if self.pages_f is not None:
            self.pages_f.close()
            self.templates_f.close()
            self.pages_f = None
            self.templates_f = None

    def __del__(self):
        #WikipediaParser.__del__(self)  # Doesn't work
        self.close()

class MyStopException(Exception):
    pass

class SyntaxException(Exception):
    pass

from mwlib import parser
class NodeHandler:
    ws_replacer_in_link = re.compile(r"\s+", re.UNICODE)

    def __init__(self):
        self.tokens = [[]]
    
    def handle(self, node):
#        print str(type(node)) + " " + str(node)
        if isinstance(node, parser.Chapter):
            self._handle_chapter(node)
        
        elif isinstance(node, parser.TagNode):
            self._handle_tagnode(node)
        
        elif isinstance(node, parser.Link):
            if isinstance(node, parser.ArticleLink):
                self._handle_article_link(node)
            elif isinstance(node, parser.CategoryLink):
                self._handle_category_link(node)
            elif isinstance(node, parser.ImageLink):
                self._handle_image_link(node)
            elif isinstance(node, parser.InterwikiLink):
                self._handle_interwiki_link(node)
            elif isinstance(node, parser.LangLink):
                self._handle_lang_link(node)
            elif isinstance(node, parser.NamespaceLink):
                self._handle_namespace_link(node)
            else:
                raise Exception("Unhandled link: %s\n" % str(node))
        
        elif  isinstance(node, parser.Paragraph):
            self._handle_paragraph(node)
            
        elif isinstance(node, parser.Section):
            self._handle_section(node)
        
        elif isinstance(node, parser.Style):
            self._handle_style(node)
        
        elif isinstance(node, parser.Text):
            self._handle_text(node)
        
        elif isinstance(node, parser.Table):
            self._handle_table(node)

        elif isinstance(node, parser.Row):
            self._handle_row(node)
        
        elif isinstance(node, parser.Cell):
            self._handle_cell(node)
 
        elif isinstance(node, parser.ItemList):
            self._handle_itemlist(node)

        elif isinstance(node, parser.Item):
            self._handle_item(node)

        elif isinstance(node, parser.Caption):
            self._handle_caption(node)
 
        else:
            self._handle_default(node)
            
    def _handle_default(self, node):
#        print "handle_default"
        for child in node.children:
            if child is not None:
                self.handle(child)
    
    def _handle_with_sentence_split(self, node):
#        print "_handle_with_sentence_split"
        if len(self.tokens) > 0 and len(self.tokens[-1]) != 0:
            self.tokens.append([])
        for child in node.children:
            self.handle(child)
        self.tokens.append([])

    def _handle_article_link(self, link):
#        print "handle_article_link"
        self._handle_links_that_matter(link)

    def _handle_category_link(self, link):
#        print "handle_category_link"
        pass

    def _handle_image_link(self, link):
        self._handle_with_sentence_split(link)

    def _handle_interwiki_link(self, link):
#        print "handle_interwiki_link"
        self._handle_links_that_matter(link)

    def _handle_lang_link(self, link):
#        print "handle_lang_link"
        pass

    def _handle_namespace_link(self, link):
#        print "handle_namespace_link"
        pass

    def _handle_links_that_matter(self, link):
#        print "_handle_links_that_matter"
        def _search_for_caption(node):
            for child in node.children:
                if isinstance(child, parser.Text):
                    return child.caption
                else:
                    caption = _search_for_caption(child)
                    if caption is not None:
                        return caption
            return None

        target = NodeHandler.ws_replacer_in_link.sub(" ", link.target, re.UNICODE)        
        caption = _search_for_caption(link)
        if caption is None:
            caption = target
        else:
            caption = NodeHandler.ws_replacer_in_link.sub(" ", caption, re.UNICODE)
#        print u"target={0} caption={1}".format(target, caption).encode('utf-8')
        self.tokens[-1].append((caption, "B-link", target))
        
    def _handle_paragraph(self, paragraph):
#        print "handle_paragraph"
        self._handle_with_sentence_split(paragraph)

    def _handle_section(self, section):
#        print "handle_section"
        self._handle_with_sentence_split(section)
    
    def _handle_style(self, style):
#        print "handle_style"
        self._handle_default(style)
    
    def _handle_text(self, text):
#        print "handle_text: " + unicode(text.caption).encode('utf-8')
        #raise NotImplementedError("Remove tokenization.")
        t = text.caption
        self.tokens[-1].append((t, "text", "0"))
    
    def _handle_table(self, table):
#        print "handle_table"
        self._handle_with_sentence_split(table)
    
    def _handle_row(self, row):
#        print "handle_row"
        self._handle_with_sentence_split(row)
    
    def _handle_cell(self, cell):
#        print "handle_cell"
        self._handle_with_sentence_split(cell)
    
    def _handle_itemlist(self, itemlist):
#        print "handle_itemlist"
        self._handle_with_sentence_split(itemlist)
    
    def _handle_item(self, item):
#        print "handle_item"
        self._handle_with_sentence_split(item)
    
    def _handle_caption(self, caption):
#        print "handle_caption"
        self._handle_with_sentence_split(caption)
    
    def _handle_tagnode(self, tagnode):
#        print "handle_tagnode"
        #print tagnode.__dict__
        if tagnode.caption == "br":
            self.tokens[-1].append(("\n", "text", "0"))
            return
        self._handle_default(tagnode)

if __name__ == '__main__':
    option_parser = OptionParser()
    option_parser.add_option("-l", "--language", dest="language",
            help="the Wikipedia language code. Default is en.", default="en")
    options, args = option_parser.parse_args()

    lt = LanguageTools(args[0], options.language)
    input_file = open(args[1], "r")
    pages_file = open(args[2], "w")
    templates_file = open(args[3], "w")

    w = WikitextToConll(lt, args[0], pages_file, templates_file)
    w.process_file(input_file)

    #import cProfile
    #cProfile.run("main()")

