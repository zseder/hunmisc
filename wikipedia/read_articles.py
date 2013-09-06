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


import re

def read_articles(istream):
    sep = "%%#PAGE"
    articles = {}

    article = ""
    title = ""
    for l in istream:
        if l.startswith(sep):
            if len(article) > 0:
                articles[title.decode("utf-8")] = article.decode("utf-8")
            article = ""
            title = re.split("\s", l.strip(), 1)[1]
        else:
            article += l
    return articles
