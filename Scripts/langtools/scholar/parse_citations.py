import sys
import urllib


def from_titlebox_get_title(title_box):

	link_title = title_box.split('<a href=')[1].split("</a>")[0]
        title = link_title.split('>')[1]
        return title


def from_citation_box_get_citation(citation_box):

	link_title = citation_box.split('a class="cit-dark-link" href=')[1].split("</a>")[0]
	link = link_title.split('>')[0]
	return link      


def from_row_get_title_citation(row):

	title_box = row.split('<td id="col-title">')[1].split('</td>')[0]	
        title = from_titlebox_get_title(title_box)
        citation_box = row.split('<td id="col-citedby">')[1].split('</td>')[0]
        if citation_box == '':
		return title, None
                
        else:
        	citation = from_citation_box_get_citation(citation_box)[1:-1] 
        	return title, citation          

        
def from_html_get_titles_citations(string):
	
        titles_citations = []
	table = string.split('<table class="cit-table">')[1].split('</table>')[0]
        rows = table.split('<tr class="cit-table item">')
        for index,row in enumerate(rows[1:]):
                if from_row_get_title_citation(row)[1] == None:
			break
                else:
	    	    title_citation = from_row_get_title_citation(row) 	  
               	    titles_citations.append(title_citation)
        return titles_citations


def main():
        
        url = urllib.urlopen(sys.argv[1]) 
	html = url.read()
        g = open("check_html", 'w')
        g.write(html)
        titles_citations = from_html_get_titles_citations(html)
        for pair in titles_citations:
        	title, link = pair
        	print title + "\t" + link 

         
main()







