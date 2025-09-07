#!/usr/bin/env python3

import autocli

args = autocli.parse(
    """
    This app adds two numbers and prints their sum

        $ python sum.py 1 2
        3
    """
)

print(args[0] + args[1])