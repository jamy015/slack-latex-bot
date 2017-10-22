from urllib.parse import quote, quote_plus
import requests

with open('default_preamble.txt') as default_preamble_file:
    default_preamble = default_preamble_file.read()


def urlencode(query, quote_via=quote_plus):
    """Encode a dict into a URL query string

    This is a homebrew implementation of the urllib.parse.urlencode function. It's necessary because the quote_via
    parameter of urlencode(), which is needed to prevent spaces being encoded as '+' signs (see
    https://github.com/jamy015/slack-latex-bot/issues/4), only showed up in Python 3.5. Because Elastic Beanstalk is
    still at Python 3.4, we have to use this ugly workaround :(

    Once we can run in a Python 3.5 (or higher) environment (i.e. once Elastic Beanstalk updates to Python 3.5), we'll
    be able to get rid of this and use the real urlencode().

    This implementation is based on https://stackoverflow.com/a/42460165/
    """
    return '&'.join(['{}={}'.format(quote_via(k), quote_via(v)) for k, v in query.items()])


def quicklatex(formula, preamble=default_preamble, show_errors=False):
    """Given a LaTeX formula, return an image URL"""
    r = requests.post('http://quicklatex.com/latex3.f', data=urlencode({
        'formula': formula,
        'preamble': preamble,
        'fsize': '19px',
        'out': '1',  # output PNG
        'errors': '1' if show_errors else '0',
    }, quote_via=quote))  # quote_via=quote ensures that any spaces won't get encoded as + signs
                          # see https://docs.python.org/3.6/library/urllib.parse.html#urllib.parse.urlencode
                          # and https://github.com/jamy015/slack-latex-bot/issues/4

    if r.status_code != 200:
        raise HTTPError(r.status_code)

    lines = r.text.split('\r\n', 2)
    if lines[0] == '0':
        return lines[1].split(' ')[0]
    else:
        raise ValueError(lines[2].rstrip())


class HTTPError(RuntimeError):
    """Raise if QuickLaTeX returns a non-200 HTTP status code"""
