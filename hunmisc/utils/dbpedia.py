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


def get_entity_from_line(l):

    entity = l.split('>')[0].split('/')[-1]
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

def select_category(block):

    category_list = []
    for l in block:
        cat = get_category_from_line(l)
        if cat != None:
            category_list.append(get_category_from_line(l))
            
    return  select_main_category(category_list)    
        

def generate_entity_blocks(file_handler):
    
    prev_entity = ''
    block  = []
    for l in file_handler:
        if l.startswith('#'):
            continue
        entity = get_entity_from_line(l)
        if (entity != prev_entity) and (prev_entity != ''):
            yield prev_entity, block
            block  = []
        block.append(l.strip())    
        prev_entity = entity


def parse(file_handler):

    for entity, block in generate_entity_blocks(file_handler): 
        category = select_category(block)
        yield entity, category

def main():

    
    for item in parse(sys.stdin):
        entity, category = item
        print entity + '\t' + category


if __name__ == "__main__":  
    main()

