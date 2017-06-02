import requests

with open('default_preamble.txt') as default_preamble_file:
    default_preamble = default_preamble_file.read()


def to_image_url(formula, preamble=default_preamble):
    """Given a LaTeX string, return an image URL"""
    r = requests.post('http://quicklatex.com/latex3.f', data={
        'formula': formula,
        'preamble': preamble,
        'out': '1',  # output PNG
        'errors': '1',
    })
    lines = r.text.split('\r\n', 2)

    if lines[0] == '0':
        return lines[1].split(' ')[0]
    else:
        raise ValueError(lines[2].rstrip())
