"""Splits an input file (from stdin) into different files named
by the language that the article belongs to.
Articles should be separated by %%#PAGE, usually an autocorpus
output with this separator should be ok
"""
import sys
from collections import defaultdict

def split_inc(istream):
    article = []
    sep = "%%#PAGE"
    articles = defaultdict(list)
    for l in istream:
        if l.startswith(sep):
            if (len(article) > 0 and len(article[0].split("/")) > 1):
                lang = article[0].split("/")[1].strip()
                articles[lang].append(article)
            article = [l]
        else:
            article.append(l)
    return article

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

def main():
    articles = split_inc(sys.stdin)
    write_articles_to_files(articles)

if __name__ == "__main__":
    main()
