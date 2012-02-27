"""Miscellaneous functions and classes."""

def ispunct(s):
    """Returns @c True, if all characters in @p s are punctuation marks."""
    for c in s:
        if c.isalnum():
            return False
    return True

# http://en.wikipedia.org/wiki/Quotation_mark_glyphs.
__quotationMarks = set(
        u'\u0022\u0027\u00AB\u00BB\u2018\u2019\u201A\u201B\u201C\u201D' +
        u'\u201E\u201F\u2039\u203A\u300C\u300D\u300E\u300F\u301D\u301E' +
        u'\u301F\uFE41\uFE42\uFE43\uFE44\uFF02\uFF07\uFF62\uFF63')
__wikiGarbage = set(u'|[]{}<>-*=')
__quotationWikiGarbage = __quotationMarks | __wikiGarbage

def isquot(s):
    """Returns @c True if all characters in @p s are quotation marks."""
    for c in s:
        if not c in __quotationMarks:
            return False
    return True

def remove_quot_from_word(token):
    """Removes quotation marks from the word and returns both the word and
    the removed quotation marks as separate tokens in a list."""
    return remove_unwanted_characters_from_word(token, __quotationMarks)

def remove_quot_and_wiki_crap_from_word(token):
    """Removes quotation marks and wiki garbage characters from the word and
    returns both the word and the removed characters as separate tokens in a
    list."""
    return remove_unwanted_characters_from_word(token, __quotationWikiGarbage)

def remove_unwanted_characters_from_word(token, unwanted_set):
    """Removes the characters @p unwanted_set from around the word and
    returns both the word and the removed characters as separate tokens in a
    list."""
    if ispunct(token):
        return [token]
    else:
        ret, after = [], []
        begin, end = 0, 0
        for i in xrange(0, len(token)):
            if token[i] in unwanted_set:
                ret.append(token[i])
            else:
                begin = i
                break

        for i in xrange(len(token) - 1, begin - 1, -1):
            if token[i] in unwanted_set:
                after.append(token[i])
            else:
                end = i + 1
                break

        print u'RET {0}[{1}:{2}]'.format(token, begin, end).encode('utf-8')
        ret.append(token[begin:end])
        after.reverse()
        ret += after

        return ret

