import sys
import re
from collections import defaultdict

def unescape(string):

    without_outer_quotation = string[1:-1]
    reescaped = without_outer_quotation.decode('string-escape')
    reescaped_without_tab = reescaped.replace('\t', ' ')

    return reescaped_without_tab


def generate_object_dicts(file_handler):
    
    needed_line_patt = re.compile('ns:m\.')
    for j in range(8):
    #first 8 lines of dump is not needed
        l = file_handler.readline()
    first = True
    old_sub = ''
    info_dict = defaultdict(list)

    for l in file_handler:

        if needed_line_patt.match(l) is None:
            continue
        sub, pred, obj = l.strip('\n').split('\t')
        if sub != old_sub and first == False:
            yield info_dict
            info_dict.clear()
        old_sub = sub
        info_dict[pred].append(obj)
        if first:
            first = False

    yield info_dict   

def get_domains(info_dict):

    domains = set([])
    for string in info_dict['ns:type.object.type']:
        domain = string.split(':')[1].split('.')[0]
        if domain != 'common' and domain != 'type' and domain != 'base' and domain != 'm':
            domains.add(domain)
    if domains == set([]): 
        return None
    else:
        return list(domains)

def get_variant_names(info_dict):

    vn = defaultdict(list)
    for string in info_dict['ns:type.object.name']:
        name_string, lang_string = '@'.join(string.split('@')[:-1]), string.split('@')[-1]
        lang = lang_string[:-1]
        name = unescape(name_string)
        vn[name].append(lang) 
            
    return vn    



def parse(file_handler):
   
    for info_dict in generate_object_dicts(file_handler):
        freebase_domains = get_domains(info_dict)       
        if freebase_domains != None:
            variant_names = get_variant_names(info_dict)
            for var in variant_names:
                lang_list = variant_names[var]
                yield var, lang_list, freebase_domains


def main():

    file_handler = sys.stdin

    for named_entity, lang_list, domain_list in parse(file_handler):
        print named_entity + '\t' + ' '.join(lang_list) + '\t' + ' '.join(domain_list)

    file_handler.close()

if __name__ == "__main__":
    main()
