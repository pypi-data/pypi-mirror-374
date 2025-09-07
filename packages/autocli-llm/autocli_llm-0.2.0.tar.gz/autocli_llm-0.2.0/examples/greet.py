#!/usr/bin/env python3

import autocli

args = autocli.parse(
    """
    This app greets the given name defaulting to "Earthling" and
    appends excitement number of exclamation marks.
    
        $ python greet.py --name Alice --excitement 3
        Hello, Alice!!!
        
        $ python greet.py
        Hello, Earthling!
    """
)

name = args.name if hasattr(args, 'name') and args.name else "Earthling"
excitement = args.excitement if hasattr(args, 'excitement') and args.excitement else 1

if isinstance(excitement, str):
    try:
        excitement = int(excitement)
    except ValueError:
        excitement = 1

if excitement < 1:
    print(f"ERROR: The value for EXCITEMENT is too low. The lowest value is 1.")
    exit(1)

print(f"Hello, {name}{'!' * excitement}")