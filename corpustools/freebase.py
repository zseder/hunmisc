"""
Copyright 2011-13 Attila Zseder
Email: zseder@gmail.com

This file is part of hunmisc project
url: https://github.com/zseder/hunmisc

hunmisc is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
"""


import sys
from collections import defaultdict

def unescape(string):

    without_outer_quotation = string[1:-1]
    reescaped = without_outer_quotation.decode('string-escape')
    reescaped_without_tab = reescaped.replace('\t', ' ')
    reescaped_without_newline = reescaped_without_tab.replace('\n', ' ')

    return reescaped_without_newline


def generate_object_dicts(file_handler):
    
    first = True
    old_sub = ''
    info_dict = defaultdict(list)

    for l in file_handler:

        if l[:5] != 'ns:m.':
            continue

        sub, pred, obj = l.strip('\n').split('\t')
        if sub != old_sub and first == False:
            yield old_sub, info_dict
            info_dict.clear()
        old_sub = sub
        info_dict[pred].append(obj)
        if first:
            first = False

    yield old_sub, info_dict   

def get_types_domains(info_dict):

    domains = set([])
    types = set([])
    for string in info_dict['ns:type.object.type']:
        domain = string.split(':')[1].split('.')[0]
        typ = string.split(':')[1].split('.')[1]
        if domain != 'common' and domain != 'type' and domain != 'base' and domain != 'm'\
           and domain != 'freebase' and domain != 'user':
            domains.add(domain)
            types.add(typ)
    if domains == set([]): 
        return None
    else:
        return list(types), list(domains)

def get_all_types(info_dict):

    proper_types = set([])
    types = set([])
    for string in info_dict['ns:type.object.type']:
        typ = string.split(':')[1].split('.')[1]
        domain = string.split(':')[1].split('.')[0]
        types.add(typ)
        if domain != 'common' and domain != 'type' and domain != 'base' and domain != 'm'\
           and domain != 'freebase' and domain != 'user':
            proper_types.add(typ)
    return list(types), list(proper_types)


def get_variant_names(info_dict):

    vn = defaultdict(list)
    for string in info_dict['ns:type.object.name']:
        name_string, lang_string = '@'.join(string.split('@')[:-1]), string.split('@')[-1]
        lang = lang_string[:-1]
        name = unescape(name_string)
        vn[name].append(lang) 
            
    return vn    

def get_name(info_dict, code):

    for string in info_dict['ns:type.object.name']:
        name_string, lang_string = '@'.join(string.split('@')[:-1]), string.split('@')[-1]
        lang = lang_string[:-1]
        if lang == code:
            return unescape(name_string)
    return ''    

def get_aliases(info_dict):

    aliases = []
    for string in info_dict['ns:common.topic.alias']:
        name_string, lang_string = '@'.join(string.split('@')[:-1]), string.split('@')[-1]
        lang = lang_string[:-1]
        name = unescape(name_string)
        aliases.append((name.decode('utf-8'), lang))    

    return aliases


def get_dict(filehandler):

    dictionary = {}
    for l in filehandler:
        k, v = l.strip().split('\t')[0], l.strip().split('\t')[1]
        dictionary[k] = v

    return dictionary    

def parse(file_handler):
    
    for item in generate_object_dicts(file_handler):
        freebase_code, info_dict = item
        lista = local_parse(info_dict)
        if lista != []:
             for item in lista:
                 variant, lang_list, freebase_domains, freebase_types, aliases = item
                 yield variant, lang_list, freebase_domains, freebase_types, aliases, freebase_code


def local_parse(info_dict):
        

        type_domain_infos = get_types_domains(info_dict)

        if type_domain_infos != None:
            freebase_types, freebase_domains = type_domain_infos

        else:
            return []

        variant_names = get_variant_names(info_dict)
        aliases = get_aliases(info_dict)
        lista = []
        for var in variant_names:
            lang_list = variant_names[var]
            lista.append((var.decode('utf-8'), lang_list, freebase_domains, freebase_types, aliases))
        return lista



def get_notable(type_name_dict, type_domain_dict, domain_name_dict, info_dict, freebase_code):
    if 'ns:common.topic.notable_types' not in info_dict:
        notable_type = 'not found'
        notable_domain = 'not found'

    else:
        #looks for notable type
        notable_type_code = info_dict['ns:common.topic.notable_types'][0][:-1] 

        if notable_type_code not in type_name_dict:
            notable_type = 'not found'
            sys.stderr.write('notable_type_code:{0} of entity {1} not in type_name_dict\n'.format(notable_type_code,
                                                                                                  freebase_code))

        else:   
            notable_type = type_name_dict[notable_type_code]

        #looks for notable domain

        if notable_type_code not in type_domain_dict:
            notable_domain = 'not found'
            sys.stderr.write('notable_type_code:{0} of entity {1} not in type_domain_dict\n'.format(notable_type_code,
                                                                                                    freebase_code))

        else:

            notable_domain_code_dotted = type_domain_dict[notable_type_code]
            notable_domain_code = notable_domain_code_dotted[:-1]
            if notable_domain_code not in domain_name_dict:
                notable_domain = 'not found'
                sys.stderr.write('notable_domain_code:{0} of entity {1} not in domain_name_dict\n'.format(notable_domain_code, 
                                                                                                          freebase_code))
            else:
                notable_domain = domain_name_dict[notable_domain_code]
    return notable_type, notable_domain    

def formatize(string):
    return string.lower().replace('_', ' ')



def get_notable_name(notable_for, type_name_dict, code_to_notable_code_dict):

    notable_for = notable_for[:-1]
    if notable_for not in code_to_notable_code_dict:
        sys.stderr.write('code -{0} - not in code_to_notable_code_dict'.format(notable_for))
        return None
    type_code = code_to_notable_code_dict[notable_for]
    type_code = type_code[:-1]
    if type_code not in type_name_dict:
        sys.stderr.write('type_code -{0} - not in type_name_dict'.format(type_code))
        return None

    return type_name_dict[type_code] 

def get_relev_type(info_dict):
    types, proper_types = get_all_types(info_dict)
    if len(proper_types) > 0:
        return proper_types[0]
    if len(types) > 0:
        return types[0]
    else:
        return 'no_type'

def parse_notable_fors(file_handler, code_to_notable_code, names_of_types):

    type_name_dict = get_dict(names_of_types)
    code_to_notable_code_dict = get_dict(code_to_notable_code)

    for item in generate_object_dicts(file_handler):
        freebase_code, info_dict = item
        if 'ns:common.topic.' in info_dict['ns:type.object.type']:
            notable_for = info_dict.get('ns:common.topic.notable_for', [''])[0]
            types, proper_types = get_all_types(info_dict)
        
            english_name = get_name(info_dict, 'en')
            if notable_for == '':
                notable_for_str = get_relev_type(info_dict)
                sys.stderr.write('no notable for to this entity\n')
            else:
                notable_for_str = get_notable_name(notable_for, type_name_dict, code_to_notable_code_dict)
                if notable_for_str == None:
                    sys.stderr.write('{0}\n'.format(freebase_code))
                    notable_for_str = get_relev_type(info_dict)
            yield freebase_code, english_name, notable_for_str        
                 

def make_replace_dicts(file_handler):

    replace_dict = defaultdict(list) 
    for l in file_handler:
        v, k = l.strip().split('\t')
        replace_dict[k[:-1]].append(v)

    return replace_dict    
        


def parse_with_noteble(file_handler, names_of_types, domains_of_types, names_of_domains, classes_of_types, replace_file):
    
    type_name_dict = get_dict(names_of_types)
    type_domain_dict = get_dict(domains_of_types)
    domain_name_dict = get_dict(names_of_domains)
    type_class_dict = get_dict(classes_of_types)
    replace_dict = make_replace_dicts(replace_file)

    for item in generate_object_dicts(file_handler):
        freebase_code, info_dict = item
        freebase_code, info_dict = item
        if 'ns:common.topic.' in info_dict['ns:type.object.type']:
            
            
            notable_type, _ = get_notable(type_name_dict, type_domain_dict,\
                                                       domain_name_dict, info_dict, freebase_code)

            if notable_type == 'not found':
                notable_type = get_relev_type(info_dict)
                
            english_name = get_name(info_dict, 'en')
            german_name = get_name(info_dict, 'de')

            notable_type_formatted = formatize(notable_type)

            if notable_type_formatted in type_class_dict:
                category = type_class_dict[notable_type_formatted]

            else:
                category = 'not categorized'
            

            yield english_name, german_name, freebase_code, notable_type_formatted, category
            for code in replace_dict[freebase_code]:
                yield english_name, german_name, code, notable_type_formatted, category


def get_type_names(file_handler):

    for item in generate_object_dicts(file_handler):
        freebase_code, info_dict = item
        if 'ns:freebase.type_profile.' in info_dict['ns:type.object.type']:
            english_name = get_name(info_dict, 'en')

            yield '{0}\t{1}'.format(freebase_code, english_name)

def get_domain_of_type(file_handler):
    for item in generate_object_dicts(file_handler):
        freebase_code, info_dict = item
        if 'ns:freebase.type_profile.' in info_dict['ns:type.object.type']:
            domain_code = info_dict['ns:type.type.domain']
            if len(domain_code) > 0:
                yield '{0}\t{1}'.format(freebase_code, domain_code[0])   


def get_domain_names(file_handler):

    for item in generate_object_dicts(file_handler):
        freebase_code, info_dict = item
        if 'ns:type.domain.' in info_dict['ns:type.object.type']:
            english_name = get_name(info_dict, 'en')
            yield '{0}\t{1}'.format(freebase_code, english_name)

def main():

    file_handler = sys.stdin
    names_of_types = open(sys.argv[1])
    domains_of_types = open(sys.argv[2])
    names_of_domains = open(sys.argv[3])
    classes_of_types = open(sys.argv[4])
    replace_file = open(sys.argv[5])

    for item in parse_with_noteble(file_handler, names_of_types, domains_of_types, names_of_domains, classes_of_types, replace_file):
        english_name, german_name, freebase_code, notable_type, category = item
        print "{0}\t{1}\t{2}\t{3}\t{4}".format(english_name, german_name, freebase_code, notable_type, category)

    file_handler.close()
    
    #code_to_notable_code = open(sys.argv[1])
    #names_of_types = open(sys.argv[2])
    #for l in parse_notable_fors(file_handler, code_to_notable_code, names_of_types):
    #    freebase_code, english_name, notable_str = l
    #    print '{0}\t{1}\t{2}'.format(freebase_code, english_name, notable_str)

if __name__ == "__main__":
    main()
