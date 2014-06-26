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
import re
from urllib import unquote

def get_entity_from_line(l):

    entity_matcher = re.search('resource/(.*?)>', l)
    entity = entity_matcher.groups()[0]
    entity = entity.decode('unicode-escape')
    entity = unquote(entity)
    entity_formatted = entity.replace('_', ' ')

    return entity_formatted

def get_category_from_line(l):

    potential_category = l.split(' ')[2]
    if potential_category.startswith('<http://dbpedia.org/ontology'):
        category = potential_category.split('>')[0].split('/')[-1]
    else:
        category = None
    return category

def select_main_category(category_list):
    # selects 2nd ontology level, if that would be Agent than 3rd
    if category_list[-1] == 'Agent':
        return category_list[-2]
    else:
        return category_list[-1]

def select_categories(block):

    category_list = []
    for l in block:
        cat = get_category_from_line(l)
        if cat != None:
            category_list.append(get_category_from_line(l))
            
    return category_list    
        
def check_if_needed(entity_string):

    needed = True
    if entity_string.endswith('  /  1') or entity_string.endswith('  /  2'):
        needed = False

    return needed

def generate_entity_blocks(file_handler):
    
    prev_entity = ''
    block  = []
    for l in file_handler:
        if l.startswith('#'):
            continue
        entity = get_entity_from_line(l)
        needed = check_if_needed(entity)
        if not needed:
            continue
        if (entity != prev_entity) and (prev_entity != ''):
            yield prev_entity, block
            block  = []
        block.append(l.strip())    
        prev_entity = entity


def parse(file_handler):

    for entity, block in generate_entity_blocks(file_handler): 
        categories = select_categories(block)
        yield entity, categories

def main():

    for item in parse(sys.stdin):
        entity, categories = item
        try:
            main_category = select_main_category(categories)
            if main_category != 'PersonFunction':
                print entity.encode('utf-8') + '\t' + main_category
        except:
            sys.stderr.write('error at {0}\n'.format(entity))


if __name__ == "__main__":  
    main()

