"""Different kinds of statistics (char, paragraph, sentence) for a wp"""
"""Exepts a wikipedia in a title/article dict (articles being in raw text)
and gives you some char/sentence/paragraph stats"""

def get_char_size(wp):
    return sum(len(a) for a in wp.itervalues())

def has_long_paragraph(article, length=450):
    return max([len(par) for par in article.split("\n")]) >= length

def get_stats(wp, char_entropy=1.0):
    total_size = get_char_size(wp)
    good_articles = dict([(t, a) for t, a in wp.iteritems()
                          if has_long_paragraph(a)])
    real_size = get_char_size(good_articles)
    real_total_ratio = float(len(good_articles)) / len(wp)
    adjusted_size = real_size * char_entropy
    return (total_size, real_size, real_total_ratio, adjusted_size)

def main():
    pass

if __name__ == "__main__":
    main()
