
from utils import *
import json
import argparse
from loadIcon import *

def main():
    parser = argparse.ArgumentParser(description="Funny JSON Explorer (FJE)")
    parser.add_argument('-f', '--file', type=str, required=True, help='Path to the JSON file')
    parser.add_argument('-s', '--style', type=str, choices=['tree', 'rectangle'], required=True, help='Visualization style: tree or rectangle')
    parser.add_argument('-i', '--icon', type=str, choices=['simple','poker'], required=True, help='Icon family: simple')
    args = parser.parse_args()

    with open(args.file, 'r') as f:
        json_data = json.load(f)

    if args.icon=='simple':
        icon_factory = SimpleIconFactory()
    elif args.icon=='poker':
        icon_factory = PokerFaceFactory()

    if args.style == 'tree':
        builder = TreeBuilder(icon_factory)
        visitor = TreeVisitor()
    elif args.style == 'rectangle':
        builder = RectangleBuilder(icon_factory)
        visitor = RectangleVisitor()


    root = builder.build(json_data)
    # visitor = ShowVisitor()
    builder.show(visitor)

if __name__ == '__main__':
    main()