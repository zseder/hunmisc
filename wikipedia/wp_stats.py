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


"""Different kinds of statistics (char, paragraph, sentence) for a wp"""
"""Exepts a wikipedia in a title/article dict (articles being in raw text)
and gives you some char/sentence/paragraph stats"""

def get_char_size(wp):
    return sum(len(a) for a in wp.itervalues())

def has_long_paragraph(article, length=450):
    return max([len(par) for par in article.split("\n")]) >= length

def get_stats(wp, char_entropy=1.0):
    res = {}
    res["total_size"] = get_char_size(wp)
    good_articles = dict([(t, a) for t, a in wp.iteritems()
                          if has_long_paragraph(a)])
    res["real_size"] = get_char_size(good_articles)
    res["real_total_ratio"] = float(len(good_articles)) / len(wp)
    res["adjusted_size"] = res["real_size"] * char_entropy
    res["articles"] = len(wp)
    goods = len(good_articles)
    if goods > 0:
        res["avg good page length"] = res["real_size"] / float(goods)
    else:
        res["avg good page length"] = 0
    return res

def main():
    pass

if __name__ == "__main__":
    main()
