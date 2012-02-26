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

def isquot(s):
    """Returns @c True if all characters in @p s are quotation marks."""
    for c in s:
        if not c in __quotationMarks:
            return False
    return True

def remove_quot_from_word(token):
    """Removes quotation marks from the word and returns both the word and
    the removed quotation marks as separate tokens in a list."""
    if ispunct(token):
        return [token]
    else:
        ret = []
        state = 0  # 0: q.marks, 1: word
        begin = 0
        for i in xrange(0, len(token)):
            if token[i] in __quotationMarks:
                if state == 0:
                    ret.append(token[i])
                else:
                    ret.append(token[begin:i])
                    ret.append(token[i])
                    state = 0
            else:
                if state == 0:
                    begin = i
                    state = 1
        if state == 1:
            ret.append(token[begin:])
    return ret

