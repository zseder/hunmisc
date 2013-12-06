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


"""Splits wikipedia incubator data (from stdin) into different files named
by the language that the article belongs to.
Articles should be separated by %%#PAGE, usually an autocorpus
output with this separator should be ok
"""
import sys
from collections import defaultdict

from read_articles import read_articles
from wp_stats import get_stats

def split_inc(articles):
    articles_by_lang = defaultdict(dict)
    for article_title, article in articles.iteritems():
        if len(article_title.split("/")) > 2:
            if article_title.split("/")[0] != "Wp":
                continue
            lang = article_title.split("/")[1].strip()
            short_title = article_title.split("/")[2].strip()
            articles_by_lang[lang][short_title] = article
    return articles_by_lang

def write_articles_to_files(articles):
    for lang in articles:
        if (lang.find(" ") >= 0 or lang.find(":") >= 0
            or lang.startswith("abusefilter")
            or not lang.islower()):
            continue

        fa = filter(lambda x: x[0].find(":") < 0, articles[lang])
        if len(fa) == 0:
            continue

        with open("{0}.incwiki".format(lang), "w") as ostream:
            for article in fa:
                for line in article:
                    ostream.write(line)

def print_stats(articles_by_lang):
    print "\t".join(["Wp_code", "Total_size", "Real_size", "real_total_ratio",
                     "adjusted_size", "articles", "avg good page length"])
    for lang in articles_by_lang:
        stats = get_stats(
            articles_by_lang[lang])
        print "\t".join(str(x) for x in [lang, stats["total_size"],
            stats["real_size"], stats["real_total_ratio"],
            stats["adjusted_size"], stats["articles"],
            stats["avg good page length"]])

def main():
    articles = read_articles(sys.stdin)
    articles_by_lang = split_inc(articles)
    print_stats(articles_by_lang)
    #write_articles_to_files(articles_by_lang)

if __name__ == "__main__":
    main()
