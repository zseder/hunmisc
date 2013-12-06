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
import time
import urllib
import os
from random import randint
from getpass import getpass

from scholar_selenium import log_into_google, get_bib_for_article, get_firefox

def from_titlebox_get_title(title_box):

    link_title = title_box.split('<a href=')[1].split("</a>")[0]
    title = link_title.split('>')[1]
    return title


def from_citation_box_get_citation(citation_box):

    link_title = citation_box.split('a class="cit-dark-link" href=')[1].split("</a>")[0]
    link, title = link_title.split('>')
    return link[1:-1], title 


def from_row_get_title_citation(row):

    title_box = row.split('<td id="col-title">')[1].split('</td>')[0]
    title = from_titlebox_get_title(title_box)
    citation_box = row.split('<td id="col-citedby">')[1].split('</td>')[0]
    if citation_box == '':
        return None 
           
    else:
        citation, anchor = from_citation_box_get_citation(citation_box) 
        try:
            count = int(anchor)
        except ValueError:
            # no citation
            return None
        return title, citation, count

        
def from_html_get_titles_citations(string):
    
    titles_citations_counts = []
    table = string.split('<table class="cit-table">')[1].split('</table>')[0]
    rows = table.split('<tr class="cit-table item">')
    for index,row in enumerate(rows[1:]):
        if from_row_get_title_citation(row) == None:
            break
        else:
            title_citation_count = from_row_get_title_citation(row)
            titles_citations_counts.append(title_citation_count)
    return titles_citations_counts


def main():

    url = urllib.urlopen(sys.argv[1]) 
    html = url.read()
    g = open("check_html", 'w')
    g.write(html)
    titles_citations_counts = from_html_get_titles_citations(html)

    username = raw_input("Enter google username\n")
    password = getpass()
    firefox = get_firefox("/home/zseder/.mozilla/firefox/dfhg1kcn.default/")
    log_into_google(firefox, username, password)
    
    for triple in titles_citations_counts:
        title, link, count = triple
        title_ascii = title.decode("utf-8").encode("ascii", "ignore").replace(" ", "_")
        num_of_lines = 0
        if os.path.exists(title_ascii):
            num_of_lines = len(open(title_ascii).readlines())
        with open(title_ascii, "a") as of:
		link = link.replace("&amp;", "&")
		for i in xrange(num_of_lines, count):
		    bib = get_bib_for_article(firefox, link + "&start={0}&num=0".format(i))
		    of.write(title + "\t" + link + "\t" + bib.replace("\n", "") + "\n")
                    time.sleep(randint(65, 80))
         
main()







