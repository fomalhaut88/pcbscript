"""
Compile into a text file:
    pcbscript compile -i 1.pcbs -o 1.txt

Compile into an SVG image:
    pcbscript draw -i 1.pcbs -o 1.svg

Compile into an SVG image and redraw it if changes happen:
    pcbscript draw -i 1.pcbs -o 1.svg --watch

Prepare a picture on a sheet of paper to print:
    pcbscript prepare -i 1.pcbs -o 1.jpg --dpi 300 --format A4
"""

import argparse
import traceback
from time import sleep

from .compiler import Compiler
from .items import serialize
from .drawer import Drawer
from .version import __version__


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('action',
                        choices=['version', 'compile', 'draw', 'prepare'])
    parser.add_argument('--input', '-i')
    parser.add_argument('--output', '-o')
    parser.add_argument('--watch', action='store_true')
    parser.add_argument('--dpi', type=int, default=300)
    parser.add_argument('--format', choices=['A4'], default='A4')
    parser.add_argument('--offset', default='0,0')
    parser.add_argument('--coef', type=float, default=1.0)
    args = parser.parse_args()
    return args


def get_code(path):
    with open(path) as f:
        return f.read()


def version(args):
    print(__version__)


def compile_(args):
    print("Fetching code...")
    code = get_code(args.input)

    print("Compiling...")
    compiler = Compiler()
    items = compiler.compile(code)

    print("Saving result...")
    with open(args.output, 'w') as f:
        for item in items:
            print(serialize(item), file=f)

    print("Completed")


def draw(args):
    if args.watch:
        print("Watching...")

        compiler = Compiler()
        drawer = Drawer()
        last_code = None

        while True:
            code = get_code(args.input)
            if code != last_code:
                try:
                    items = compiler.compile(code)
                    drawer.draw(items)
                    drawer.save(args.output)
                    print("Updated")
                except:
                    print("Error")
                    traceback.print_exc()
                finally:
                    last_code = code
            else:
                sleep(0.1)

    else:
        print("Fetching code...")
        code = get_code(args.input)

        print("Compiling...")
        compiler = Compiler()
        items = compiler.compile(code)

        print("Drawing...")
        drawer = Drawer()
        drawer.draw(items)

        print("Saving result...")
        drawer.save(args.output)

        print("Completed")


def prepare(args):
    print("Fetching code...")
    code = get_code(args.input)

    print("Compiling...")
    compiler = Compiler()
    items = compiler.compile(code)

    print("Drawing...")
    drawer = Drawer(color=(255, 255, 255), bg_color=(0, 0, 0))
    drawer.draw(items)

    print("Saving result...")
    offset = list(map(float, args.offset.split(',', 1)))
    drawer.prepare_a4(args.output, args.dpi, offset, coef=args.coef)

    print("Completed")


def main():
    args = get_args()

    if args.action == 'version':
        version(args)
    elif args.action == 'compile':
        compile_(args)
    elif args.action == 'draw':
        draw(args)
    elif args.action == 'prepare':
        prepare(args)


if __name__ == "__main__":
    main()
