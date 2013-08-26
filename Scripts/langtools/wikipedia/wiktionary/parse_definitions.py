import sys
import re
from HTMLParser import HTMLParser
import cPickle

def sort_out_abbrevs(line, abbrevs, other_patterns):

    contained = set([])
    for pair in abbrevs:
        abbrev = pair[0]
        if abbrev in line:
             contained.add(abbrev.encode('utf-8'))
             line = line.replace(abbrev, "")
        abbrev_description_pattern = "(.*)" + abbrev[:-2] + "\|([:,;])}}(.*)"    
        compiled = re.compile(abbrev_description_pattern)
        m = compiled.match(line)
        while m:
            contained.add(abbrev.encode('utf-8'))
            line = m.groups()[0] + m.groups()[1] + m.groups()[2]
            m = compiled.match(line)
    for pat in other_patterns: 
        compiled = re.compile(pat)
        m = compiled.search(line)
        while m:
            contained.add(m.group().encode('utf-8'))
            line = line[:m.start()] + line[m.end():]
            m = compiled.search(line)

    return line, contained


def sort_out_wiki_tags(line_with_wiki_tags):
    

    bracket_pattern = re.compile('\[\[([^][]*?\|){0,1}([^][]*?)\]\]')
    s = bracket_pattern.search(line_with_wiki_tags)
    while s:
        line_with_wiki_tags = line_with_wiki_tags[:s.start()] + s.groups()[1] + line_with_wiki_tags[s.end():] 
        s = bracket_pattern.search(line_with_wiki_tags)
    line_without_brackets = line_with_wiki_tags
    line_without_idezojelek = line_without_brackets.replace("''", '')
    tags_to_delete = ['Lautschrift']

    for item in tags_to_delete:
        line_without_idezojelek = re.sub('\{\{' + item + '\|.*?\}\}', '', line_without_idezojelek)

    line_without_idezojelek_u = line_without_idezojelek.decode('utf-8')

    stylistic_wiki_tags = [(u'{{ugs.}}',  u'umgangssprachlich'), (u'{{abw.}}', u'abwertend'), (u'{{va.}}', u'veraltet'), (u'{{allg.}}', u'allgemein'), (u'{{bildl.}}', u'bildlich'), (u'{{dichter.}}', u'dichterlich'), (u'{{fachspr.}}', u'fachsprachlich'), (u'{{fam.}}', u'familiar'), (u'{{geh.}}', u'gehoben'), (u'{{hist.}}', u'historisch'), (u'{{landsch.}}', u'landschaftlich'), (u'{{nordd.}}', u'norddeutsch'), (u'{{poet.}}', u'poetisch'), (u'{{reg.}}', u'regional'), (u'{{scherzh.}}u', u'scherzlich'), (u'{{schweiz.}}', u'schweiz'), (u'{{veraltend}}', u'veraltend'), (u'{{veraltet}}', u'veraltetu'), (u'{{vul.}}', u'vulgarisch'), (u'{{\xf6sterr.}}', u'{{\xf6sterreichisch}}'), (u'{{\xfcbertr.}}', u'\xfcbertragen'), (u'{{s\xfcdd.}}', u's\xfcddeutsche'), (u'{{scherzh.}}', u'scherzlich')]

    stylistic_other_patterns = ['{{Kontext|Linguistik|.*?}}']

    syntactic_wiki_tags = [(u'{{refl.}}', u'reflexiv'),(u'{{intrans.}}', u'intransitiv'), (u'{{trans.}}', u'transitiv'), (u'{{kPl.}}', u'kein Plural'), (u'{{Pl.}}', u'Plural'), (u'{{kSt.}}', u'keine Steigerung'), (u'{{Dativ}}', u'Dativ'), (u'{{Genitiv}}', 'Genitiv'), (u'{{n}}', u'neutrum'), (u'{{f}}', 'femininum'), (u'{{m}}', u'masculinum'), (u'{{Akkusativ}}', u'Akkusativ')]

    
    syntactic_other_patterns = []
    line_u, stylistic = sort_out_abbrevs(line_without_idezojelek_u, stylistic_wiki_tags, stylistic_other_patterns) 
    line_u, syntactic = sort_out_abbrevs(line_u, syntactic_wiki_tags, syntactic_other_patterns)
    
   
    return line_u.encode('utf-8'), stylistic, syntactic


def sort_out_html_like_tags(string):
    
    string_unescaped = HTMLParser().unescape(string.decode('utf-8')).encode('utf-8')
    string_without_nbsp = string_unescaped.replace('&nbsp;', '')
    string_without_ndash = string_without_nbsp.replace('&ndash;','')
    string_without_sup_tag = re.sub('<sup>.*?</sup>', '', string_without_ndash)
    string_without_sub_tag = re.sub('<sub>.*?</sub>', '', string_without_sup_tag)
    string_without_small_tag = re.sub('<small>.*?</small>', '', string_without_sub_tag)
    string_without_references_0 = re.sub('<ref.*?>.*?</ref>', '', string_without_small_tag, re.DOTALL)
    string_without_references = re.sub('<ref.*?>', '', string_without_references_0)

    return string_without_references

def sort_out_math_expressions(text):
    return re.sub('<math>.*?</math>', '_MATH_EXPR_', text)

def random_eseti_replace(text):

    todelete = ['{{Internetquelle']
    for item in todelete:
        text = text.replace(item, '')

    return text

def clean_def(text):
    text = sort_out_html_like_tags(text)
    text = sort_out_math_expressions(text)
    text = random_eseti_replace(text)

    text, stylistic, syntactic = sort_out_wiki_tags(text)
    
    return text, stylistic, syntactic

def generate_definitions(block):
    
    def_pattern = re.compile('\n:+(\[(.*?)\])?(.*)')
    def_matcher = def_pattern.search(block)
    while def_matcher:
        index, definition = def_matcher.groups()[1], def_matcher.groups()[2]
        block = block[def_matcher.end():]
        def_matcher = def_pattern.search(block)
        yield index, definition.strip()

def get_definition_part(text):

    try:
        return text.split('{{Bedeutungen}}', 1)[1].split('\n\n', 1)[0]
    except IndexError:
        return None
    
def generate_pos_parts(text):

    subtext_pattern = re.compile("=== {{Wortart\|(.*?)\|Deutsch}}((,)? {{(.*?)}})?.*? ===", re.DOTALL)
    subtext_matcher = subtext_pattern.search(text)
    while subtext_matcher:
        pos = subtext_matcher.groups()[0].strip()
        art = None
        if subtext_matcher.groups()[3] is not None:
            art = subtext_matcher.groups()[3].strip()
            if not art in ['m', 'f', 'n']:
                art = None
        leftover = text[subtext_matcher.end():]
        another_subtext_matcher = subtext_pattern.search(leftover)
        if another_subtext_matcher:
            this_text = leftover[:another_subtext_matcher.start()]
        else:
            this_text = leftover

        text = leftover

        subtext_matcher = subtext_pattern.search(text)
        yield pos, art, this_text

def generate_language_parts(text):
    
    subtext_pattern = re.compile("==.*?\({{Sprache\|(.*?)}}\) ==", re.DOTALL)
    subtext_matcher = subtext_pattern.search(text)
    while subtext_matcher:
        language = subtext_matcher.groups()[0].strip()
        leftover = text[subtext_matcher.end():]
        another_subtext_matcher = subtext_pattern.search(leftover)
        if another_subtext_matcher:
            this_text = leftover[:another_subtext_matcher.start()]
            text = leftover[another_subtext_matcher.end():]

        else:
            this_text = leftover

        subtext_matcher = another_subtext_matcher
        yield language, this_text

def generate_pages(f):
    intext = False
    for l in f:
        l = l.lstrip(' ').strip('\t')
        # title
        if l.startswith("<title>"):
            title = l.split("<title>")[1].split("</title>")[0]
        
        # one-line text fragment
        if l.startswith("<text") and l.rstrip().endswith("</text>"):
            text = l.split(">", 1)[1].split("<", 1)[0]
            continue

        # text starter
        if l.startswith("<text"):
            intext = True
            text = l.split(">", 1)[1].split("<", 1)[0]
            l = text
            continue

        # text end tag
        if l.rstrip().endswith("</text>"):
            intext = False
            text += l.replace("</text>", "").rstrip()
            yield title, text

        # inside text
        if intext:
            text += l
            

def main():
    data_file = open(sys.argv[1])
    d = {}
    for title, text in generate_pages(data_file):
        if ":" in title:
            continue
        
        if title not in d:
            d[title] = []
        #print "Wort", title
        for language, langtext in generate_language_parts(text):
            if language != "Deutsch":
                continue

            for pos, art, postext in generate_pos_parts(langtext):
                definition_block = get_definition_part(postext)
                if definition_block == None:
                    continue
                d[title].append((pos, art, []))
                for index, definition in generate_definitions(definition_block):
                    cleaned_def, syntactic_tags, stylistic_tags = clean_def(definition)
                    d[title][-1][2].append((";".join(list(syntactic_tags)), ";".join(list(stylistic_tags)), index, cleaned_def))
    
    cPickle.dump(d, open(sys.argv[2], "w"))
                
main()    
