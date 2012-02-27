"""Parameters: the configuration file, the two outputs: the pages and the
templates files."""
# TODO: ' to separate token (currently it is not removed from the beginning of
#       words).

import re
import sys
from optparse import OptionParser
from itertools import chain
from langtools.utils.misc import remove_quot_and_wiki_crap_from_word
from langtools.utils.language_config import LanguageTools

parser = OptionParser()
parser.add_option("--hunpos_model", dest="hunpos_model",
                  help="the hunpos model file. Default is $HUNPOS/english.model",
                  metavar="MODEL_FILE")
parser.add_option("--hunpos_encoding", dest="hunpos_encoding",
                  help="the encoding used by the hunpos model file. Default is utf-8",
                  default='utf-8')
parser.add_option("-l", "--language", dest="language",
                  help="the Wikipedia language code. Default is en.", default="en")
parser.add_option("-a", "--abbrevs", dest="abbrevs",
                  help="abbreviations file.")
options, args = parser.parse_args()

lt = LanguageTools(args[0], options.language)

pages_file = open(args[1], "w")
templates_file = open(args[2], "w")
abbrevs = None
if options.abbrevs is not None:
    abbrevs = set((l.strip() for l in file(options.abbrevs)))
options.ocamorph_runnable = 1

from langtools.nltk.nltktools import NltkTools
if options.ocamorph_runnable is not None:
    nt = NltkTools(tok=True, abbrev_set=abbrevs)
else:
    nt = NltkTools(tok=True, pos=True, stem=True, pos_model=options.hunpos_model, abbrev_set=abbrevs)

ws_stripper = re.compile(r"\s*", re.UNICODE)
ws_replacer_in_link = re.compile(r"\s+", re.UNICODE)

class MyStopException(Exception):
    pass

class SyntaxException(Exception):
    pass

skiplist = []
try:
    skiplist_file = file(sys.argv[1])
    for line in skiplist_file:
        skiplist.append(line.strip())
except:
    pass

def remove_xml_comments(text):
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

def remove_open_close(text, openstr, closestr):
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

def remove_open_close_lame(text, openstr, closestr):
    while True:
        open = text.find(openstr)
        close = text.find(closestr, open)
        if open > -1 and close > -1:
            text = text[:open] + text[close + len(closestr):]        
        else:
            break
    return text

def tokenize_part(tokens):
    def __search_for_right_index(old_index, index_inside_old_token):
        good = False
        while not good:
            my_token = tokens[old_index][0][index_inside_old_token:]
            index_inside_old_token += len(ws_stripper.match(my_token).group(0))
            if index_inside_old_token == len(tokens[old_index][0]):
                old_index += 1
                index_inside_old_token = 0
            else:
                good = True
        
        return old_index, index_inside_old_token
    
    part_string = "".join((t[0] for t in tokens))
    #print tokens
    #print part_string.encode("utf-8")
    text = nt.tokenize(part_string)
    #print [s for s in text]
    new_tokens = []
    old_index = 0
    index_inside_old_token = 0
    inside_link = False
    for sen in text:
        actual_sentence = []
        sen2 = []
        for tok in sen:
            if tok != ". . .":
                sen2.append(tok)
            else:
                sen2 += [".", ".", "."]
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
                    print tok.encode("utf-8")
                    print tokens[old_index][0].encode("utf-8")
                    print tokens[old_index][0][index_inside_old_token:index_inside_old_token+(len(tok))].encode("utf-8")
                    raise Exception("New token is longer than old one!")
        
        if len(actual_sentence) > 0:
            new_tokens.append(actual_sentence)
    return new_tokens

def tokenize_all(tokens):
    new_tokens = []
    for part in tokens:
        for dbl in tokenize_part(part):
            dbl = list(chain.from_iterable([[w] + l[1:] for w in remove_quot_and_wiki_crap_from_word(l[0])] for l in dbl))
            new_tokens.append(dbl)

    return new_tokens

def add_pos_tags(tokens):
    for sen_i, sen in enumerate(tokens):
        tagged_sen = nt.pos_tag([tok[0].encode(options.hunpos_encoding) for tok in sen])
        for tok_i, tagged_tok in enumerate(tagged_sen):
            try:
                tok, pos = [x.decode(options.hunpos_encoding) for x in tagged_tok]
            except ValueError:
                continue
            tokens[sen_i][tok_i].append(pos)

def add_stems(tokens):
    for sen_i, sen in enumerate(tokens):
        stemmed = nt.stem(((tok[0], tok[3]) for tok in sen))
        hard_stemmed = nt.stem((((tok[0][0].lower() + tok[0][1:] if tok[0][0].isupper() and tok[0][1:].islower() else tok[0]), tok[3]) for tok in sen))
        for tok_i, (tok_stemmed, tok_hard_stemmed) in enumerate(zip(stemmed, hard_stemmed)):
            tokens[sen_i][tok_i].append(tok_stemmed[2])
            tokens[sen_i][tok_i].append(tok_hard_stemmed[2])

def add_pos_and_stems(tokens):
    """If the ocamorph parameters are specified, the huntools are used for
    POS'ing and stemming, otherwise we fall back to the hunpos and the
    standard NLTK stemmer."""
    if options.ocamorph_runnable is not None:
        lt.pos_tag(tokens)
    else:
        add_pos_tags(tokens)
        add_stems(tokens)

from mwlib import parser
class NodeHandler:
    def __init__(self):
        self.tokens = [[]]
    
    def handle(self, node):
        print str(type(node)) + " " + str(node)
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
        for child in node.children:
            if child is not None:
                self.handle(child)
    
    def _handle_with_sentence_split(self, node):
        self.tokens.append([])
        for child in node.children:
            self.handle(child)
    
    def _handle_article_link(self, link):
        self._handle_links_that_matter(link)

    def _handle_category_link(self, link):
        pass

    def _handle_image_link(self, link):
        for child in link.children:
            if isinstance(child, parser.Text):
                self.tokens.append([])
                self.handle(child)

    def _handle_interwiki_link(self, link):
        self._handle_links_that_matter(link)

    def _handle_lang_link(self, link):
        pass

    def _handle_namespace_link(self, link):
        pass

    def _handle_links_that_matter(self, link):
        def _search_for_caption(node):
            for child in node.children:
                if isinstance(child, parser.Text):
                    return child.caption
                else:
                    caption = _search_for_caption(child)
                    if caption is not None:
                        return caption
            return None

        target = ws_replacer_in_link.sub(" ", link.target, re.UNICODE)        
        caption = _search_for_caption(link)
        if caption is None:
            caption = target
        else:
            caption = ws_replacer_in_link.sub(" ", caption, re.UNICODE)
        print u"target={0} caption={1}".format(target, caption).encode('utf-8')
        self.tokens[-1].append((caption, "B-link", target))
        
    def _handle_paragraph(self, paragraph):
        self._handle_with_sentence_split(paragraph)

    def _handle_section(self, section):
        self._handle_with_sentence_split(section)
    
    def _handle_style(self, style):
        self._handle_default(style)
    
    def _handle_text(self, text):
        #raise NotImplementedError("Remove tokenization.")
        t = text.caption
        self.tokens[-1].append((t, "text", "0"))
    
    def _handle_table(self, table):
        self._handle_with_sentence_split(table)
    
    def _handle_row(self, row):
        self._handle_with_sentence_split(row)
    
    def _handle_cell(self, cell):
        self._handle_with_sentence_split(cell)
    
    def _handle_itemlist(self, itemlist):
        self._handle_with_sentence_split(itemlist)
    
    def _handle_item(self, item):
        self._handle_with_sentence_split(item)
    
    def _handle_caption(self, caption):
        self._handle_with_sentence_split(caption)
    
    def _handle_tagnode(self, tagnode):
        #print tagnode.__dict__
        if tagnode.caption == "br":
            self.tokens[-1].append(("\n", "text", "0"))
            return
        self._handle_default(tagnode)

page_separator = "%%#PAGE"

def write_templates_into_f(raw, f):
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

def parse_actual_page(actual_page, actual_title, pages_f, templates_f):
    from mwlib.uparser import parseString, simpleparse
    from mwlib.expander import get_templates

    s = remove_xml_comments(actual_page)
    try:
        s = remove_open_close(s, "<math>", "</math>")
    except SyntaxException, se:
        s = remove_open_close_lame(s, "<math>", "</math>")
        sys.stderr.write(u"Problems with <math>: {0}\n".format(actual_title).encode("utf-8"))
    
    templates = get_templates(s)
    templates_f.write(u"{0} {1}\n".format(page_separator, actual_title).encode("utf-8"))
    if not write_templates_into_f(s, templates_f):
        sys.stderr.write(u"Problems with templates and mwparser: {0}\n".format(actual_title).encode("utf-8"))
    
    try:
        s = remove_open_close(s, "{{", "}}")
    except SyntaxException:
        s = remove_open_close_lame(s, "{{", "}}")
        sys.stderr.write(u"Problems with braces: {0}\n".format(actual_title).encode("utf-8"))
    try:
        #r=simpleparse(raw=s)
        #quit()
        r=parseString(raw=s, title=actual_title, lang=options.language)
    except AssertionError:
        sys.stderr.write(u"AssertionError problem: {0}\n".format(actual_title).encode("utf-8"))
        return
    except ImportError, e:
        sys.stderr.write(u"ImportError problem({0}): {1}\n".format(e, actual_title).encode("utf-8"))
        return
    except AttributeError, e:
        excepted_error_message = "'ImageMap' object has no attribute 'imagelink'"
        if str(e).strip() == excepted_error_message:
            sys.stderr.write(u"imagemap/imagelink error: {0}\n".format(actual_title).encode("utf-8"))
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
            sys.stderr.write(u"Maximum depth recursion at site: {0}\n".format(actual_title).encode("utf-8"))
            return
    tokens = tokenize_all(tokens)
    add_pos_and_stems(tokens)
    
    pages_f.write(u"{0} {1}\n".format(page_separator, actual_title).encode("utf-8"))
    pages_f.write(u"{0}\t{1}\n".format("Templates:", u",".join((t.strip().replace("\n", "") for t in templates))).encode("utf-8"))
    
    for sen in tokens:
        for t in sen:
            try:
                pages_f.write(u"\t".join(t).encode("utf-8") + "\n")
            except UnicodeError, ue:
                print "Trying to print: "
                for w in t:
                    if isinstance(w, unicode):
                        print w.encode('utf-8')
                    else:
                        print w
                raise ue
        pages_f.write("\n")

actual_page = u""
actual_title = u""
skip = False
for line in sys.stdin:
    line = line.decode("utf-8")
    if line.startswith(page_separator):
        if actual_page != u"" and not skip:
            parse_actual_page(actual_page, actual_title, pages_file, templates_file)
        actual_page = u""
        try:
            actual_title = line.strip().split(" ", 1)[1]
        except IndexError:
            sys.stderr.write("Page title contains only whitespace\n")
            skip = True
        if  actual_title.find(":") >= 0 or actual_title in skiplist:
            skip = True
        else:
            skip = False
    else:
        actual_page += line

if len(actual_page) > 0:
    parse_actual_page(actual_page, actual_title, pages_file, templates_file)

