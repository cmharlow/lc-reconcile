"""
Taken from the Helmut project.
https://github.com/okfn/helmut/blob/master/helmut/text.py
In process of being reviewed, modified, for LoC optimization.
"""

from unicodedata import normalize as ucnorm, category


def normalize(text: str) -> str:
    if not isinstance(text, str):
        str(text, 'utf-8')
    text = text.lower()
    decomposed = ucnorm('NFKD', text)
    filtered = []
    # TODO replace this home grown diacritic folding with standard function?
    for char in decomposed:
        cat = category(char)
        if cat.startswith('C'):
            filtered.append(' ')
        elif cat.startswith('M'):
            # skip marks, such as umlauts
            continue
        elif cat.startswith('Z'):
            # replace newlines, non-breaking space, etc with spaces
            filtered.append(' ')
        # elif cat.startswith('S'):
            # skip symbols, such as currency
            continue
        else:
            filtered.append(char)
    text = ''.join(filtered)
    while '  ' in text:
        text = text.replace('  ', ' ')
    text = text.strip()
    return ucnorm('NFKC', text)


def url_slug(text: str) -> str:
    text = normalize(text)
    text = text.replace(' ', '-')
    text = text.replace('.', '_')
    return text


def tokenize(text: str, splits='COPZ') -> str:
    token = []
    for c in str(text, 'utf-8'):
        if category(c)[0] in splits:
            if len(token):
                yield ''.join(token)
            token = []
        else:
            token.append(c)
    if len(token):
        yield ''.join(token)
