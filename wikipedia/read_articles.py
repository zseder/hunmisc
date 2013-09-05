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
