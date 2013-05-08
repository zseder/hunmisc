"""Different kinds of statistics (char, paragraph, sentence) for a wp"""
"""Exepts a wikipedia in a title/article dict (articles being in raw text)
and gives you some char/sentence/paragraph stats"""
import sys

def get_char_size(wp):
    return sum(len(a) for a in wp.itervalues())

def has_long_paragraph(title, article, length=450):
    return True

def get_stats(wp, char_entropy=1.0):
    total_size = get_char_size(wp)
    good_articles = dict([(t, a) for t, a in wp.iteritems()
                          if has_long_paragraph(t, a)])
    real_size = get_char_size(good_articles)
    real_total_ratio = float(len(good_articles)) / len(wp)
    adjusted_size = real_size * char_entropy

def main():
    pass

if __name__ == "__main__":
    main()
