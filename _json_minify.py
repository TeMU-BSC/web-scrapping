'''
Minify json files.
Author: https://github.com/aasensios
'''

import json
import os
import ntpath

import click


@click.command()
@click.argument('src', type=click.File('r'), nargs=-1)
@click.argument('dst', type=click.Path(exists=True), nargs=1)
@click.option('--encoding', default='utf-8', help='Encoding format.')
@click.option('--ensure-ascii', default=False, help='Force to write only ASCII characters (i.e. no graphical accents allowed).')
@click.option('--separators', default=(',', ':'), help='Encoding format.')
def minify(src, dst, encoding, ensure_ascii, separators):
    '''Minify some json files.'''
    for file in src:
        with open(file.name, 'r') as f:
            content = f.read()
            data = json.loads(content)
        with open(os.path.join(dst, ntpath.basename(file.name)), 'w', encoding=encoding) as f:
            json.dump(data, f, ensure_ascii=ensure_ascii, separators=separators)


if __name__ == '__main__':
    minify()
