from argparse import ArgumentParser
from tempfile import TemporaryDirectory
from pathlib import Path
from PIL import Image
import subprocess
from pydfscanner.pydfscanner import scanner_main

END = '\x1b[0m'
PURPLE = '\x1b[35m'

def main():
    parser = ArgumentParser(
            description='''Convert a series of images to a PDF.
                           Crops and adjusts for skew and rotation''')
    parser.add_argument('files', nargs='+', type=Path,
        help='Paths to image files')
    parser.add_argument('-o', '--output', required=True, type=Path, 
        help='Path to output file')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('-n', '--no-open', action='store_true',
        help='Do not open resulting PDF')
    args = parser.parse_args()

    with TemporaryDirectory(delete=not args.debug) as tmp:
        tmp = Path(tmp)
        pages = []
        for f in args.files:
            if not f.exists(): raise SystemExit('No such file:', f)
            out = tmp / f.name
            scanner_main(str(f), str(out), args.debug)
            with Image.open(out) as im:
                pages.append(im.convert('RGB'))

        if not pages: raise SystemExit('No pages to save')
        pages[0].save(str(args.output), 'PDF', resolution=100.0, save_all=True,
                       append_images=pages[1:])

        if args.debug:
            print((
                f'{PURPLE}DEBUG{END} Intermediate files located at: '
                f'{PURPLE}{tmp}{END}'
            ))
        elif not args.no_open:
            subprocess.Popen(['xdg-open', str(args.output)])  
