"""
Taken from the Helmut project.
https://github.com/okfn/helmut/blob/master/helmut/text.py
In process of being reviewed, modified, for LoC optimization.
"""

from unicodedata import normalize as ucnorm, category

def normalize(text):
    """Standard text normalization functions."""
    if not isinstance(text, str):
        str(text, 'utf-8')
    text = text.lower()
    decomposed = ucnorm('NFKD', text)
    filtered = []
    for char in decomposed:
        cat = category(char)
        if cat.startswith('C'):
            filtered.append(' ')
        elif cat.startswith('M'):
            # marks, such as umlauts
            continue
        elif cat.startswith('Z'):
            # newlines, non-breaking etc.
            filtered.append(' ')
        # elif cat.startswith('S'):
            # symbols, such as currency
            continue
        else:
            filtered.append(char)
    text = u''.join(filtered)
    while '  ' in text:
        text = text.replace('  ', ' ')
    text = text.strip()
    return ucnorm('NFKC', text)

def url_slug(text):
    """Create a URL Slug from common query string components."""
    text = normalize(text)
    text = text.replace(' ', '-')
    text = text.replace('.', '_')
    return text

def tokenize(text, splits='COPZ'):
    """Split strings on a given token or delimiter value."""
    token = []
    for c in str(text, 'utf-8'):
        if category(c)[0] in splits:
            if len(token):
                yield u''.join(token)
            token = []
        else:
            token.append(c)
    if len(token):
        yield u''.join(token)
