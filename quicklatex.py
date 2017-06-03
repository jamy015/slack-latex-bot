import requests

with open('default_preamble.txt') as default_preamble_file:
    default_preamble = default_preamble_file.read()


def quicklatex(formula, preamble=default_preamble, show_errors=False):
    """Given a LaTeX formula, return an image URL"""
    r = requests.post('http://quicklatex.com/latex3.f', data={
        'formula': formula,
        'preamble': preamble,
        'fsize': '19px',
        'out': '1',  # output PNG
        'errors': '1' if show_errors else '0',
        })

    if r.status_code != 200:
        raise HTTPError(r.status_code)

    lines = r.text.split('\r\n', 2)
    if lines[0] == '0':
        return lines[1].split(' ')[0]
    else:
        raise ValueError(lines[2].rstrip())


class HTTPError(RuntimeError):
    """Raise if QuickLaTeX returns a non-200 HTTP status code"""
