"""Splits an input file (from stdin) into different files named
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
    for lang in articles_by_lang:
        tot_size, real_size, real_total_ratio, adjusted_size = get_stats(
            articles_by_lang[lang])
        print lang, tot_size, real_size, real_total_ratio, adjusted_size

def main():
    articles = read_articles(sys.stdin)
    articles_by_lang = split_inc(articles)
    print_stats(articles_by_lang)
    #write_articles_to_files(articles_by_lang)

if __name__ == "__main__":
    main()
