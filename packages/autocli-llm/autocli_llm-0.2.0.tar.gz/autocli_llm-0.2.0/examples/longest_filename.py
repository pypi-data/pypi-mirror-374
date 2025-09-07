#!/usr/bin/env python3

import autocli
import os

args = autocli.parse(
    """
    This app prints the file with the longest name in the given directory (default: PWD)

        $ ls /tmp
        a.txt ab.txt abc.txt

        $ python longest_filename.py --path /tmp
        abc.txt
    """
)

path = args.path if hasattr(args, 'path') and args.path else os.getcwd()

try:
    files = os.listdir(path)
    if files:
        longest = max(files, key=len)
        print(longest)
    else:
        print("No files found in directory")
except FileNotFoundError:
    print(f"Directory not found: {path}")