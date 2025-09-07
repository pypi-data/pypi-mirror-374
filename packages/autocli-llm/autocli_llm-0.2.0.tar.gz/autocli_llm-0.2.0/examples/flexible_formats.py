#!/usr/bin/env python3
"""
Demonstrates that autocli understands various CLI argument formats.
The LLM is smart enough to parse any reasonable syntax!
"""

import autocli

# Example 1: Mixed format styles
print("Example 1: Mixed formats")
args = autocli.parse(
    """
    Database connection tool that accepts various argument formats
    
    Examples:
        $ dbconnect --host="localhost" --port=5432 --user='admin' --verbose
        $ dbconnect host:localhost port:5432 user:admin -v
        $ dbconnect -h localhost -p 5432 -u admin --verbose=true
        $ dbconnect --host localhost port 5432 user admin
        $ dbconnect server=localhost port=5432 username='admin' verbose
    """
)

print(f"Host: {args.host if hasattr(args, 'host') else 'not specified'}")
print(f"Port: {args.port if hasattr(args, 'port') else 'not specified'}")
print()

# Example 2: Non-standard but clear syntax
print("Example 2: Non-standard syntax")
args = autocli.parse(
    """
    Configuration setter with unique syntax
    
    Usage:
        config set name:"Application Name" debug:true timeout:30
        config set [name=MyApp, debug=false, timeout=60]
        config set {name: "MyApp", debug: true, timeout: 45}
    """
)

# Example 3: Natural language mixed with examples
print("Example 3: Natural language description")
args = autocli.parse(
    """
    This tool processes files. You give it an input file, 
    optionally an output file, and it can run in verbose mode.
    
    For example:
        process input.txt output.txt --verbose
        process input.txt -o result.txt -v
        process file:input.txt output:result.txt verbose:true
        process --input=data.csv --output=processed.csv
    """
)

print("The LLM understands intent, not just syntax!")
print("It parses arguments regardless of format: --arg=val, -a val, arg:val, arg val, etc.")