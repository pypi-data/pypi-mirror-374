#!/usr/bin/env python3
"""
Demonstrates autocli's ability to understand various data types.
The LLM intelligently infers types from context and examples.
"""

import autocli

# Example 1: Numeric types (integers and floats)
print("=" * 50)
print("Example 1: Numeric Types")
print("=" * 50)

args = autocli.parse(
    """
    Scientific calculator with various numeric inputs
    
    Examples:
        $ calc --precision 0.001 --iterations 1000 --threshold 3.14159
        $ calc -p 0.0001 -i 500 --threshold=2.71828
        $ calc precision:0.01 iterations:100 threshold:1.618
    """
)

print(f"Precision: {args.precision if hasattr(args, 'precision') else 'default'} (float)")
print(f"Iterations: {args.iterations if hasattr(args, 'iterations') else 'default'} (integer)")
print(f"Threshold: {args.threshold if hasattr(args, 'threshold') else 'default'} (float)")
print()

# Example 2: Boolean values in various formats
print("=" * 50)
print("Example 2: Boolean Values")
print("=" * 50)

args = autocli.parse(
    """
    Build tool with boolean flags in different formats
    
    Examples:
        $ build --verbose=true --debug=false --optimize=yes --clean=no
        $ build -v 1 -d 0 --optimize=True --clean=False
        $ build verbose:yes debug:no optimize:1 clean:0
        $ build --verbose --no-debug --optimize --no-clean
    """
)

print("The LLM understands these boolean formats:")
print("  true/false, yes/no, 1/0, True/False")
print("  --flag (implies true), --no-flag (implies false)")
print()

# Example 3: Lists and enumerated types
print("=" * 50)
print("Example 3: Lists and Enumerated Types")
print("=" * 50)

args = autocli.parse(
    """
    Task scheduler that accepts days of the week and time lists
    
    Examples:
        $ schedule --days Monday,Wednesday,Friday --times 9:00,14:00,18:00
        $ schedule --days="Mon Tue Thu" --times="10:30 15:45"
        $ schedule days:[Monday,Tuesday,Wednesday] times:[9:00,17:00]
        $ schedule --days Mon,Wed,Fri --hours 9,14,18 --priority high
    """
)

print("Days can be specified as:")
print("  - Comma-separated: Monday,Wednesday,Friday")
print("  - Space-separated: 'Mon Tue Thu'")
print("  - List notation: [Monday,Tuesday,Wednesday]")
print()

# Example 4: Complex data with mixed types
print("=" * 50)
print("Example 4: Mixed Complex Types")
print("=" * 50)

args = autocli.parse(
    """
    Data processor with various configuration options
    
    Usage:
        $ process --input data.csv --output results.json \
                  --sample-rate 0.5 --max-rows 10000 \
                  --columns name,age,salary --skip-errors yes \
                  --formats csv,json,xml --compression true
        
        $ process -i input.txt -o output.txt \
                  sample-rate:0.25 max-rows:5000 \
                  columns:[id,timestamp,value] \
                  skip-errors:1 formats:"csv json parquet"
    """
)

print("The LLM correctly infers:")
print("  - File paths (strings): input, output")
print("  - Decimals (floats): sample-rate")
print("  - Whole numbers (integers): max-rows")
print("  - Lists (arrays): columns, formats")
print("  - Booleans: skip-errors, compression")
print()

# Example 5: Date and time formats
print("=" * 50)
print("Example 5: Dates and Times")
print("=" * 50)

args = autocli.parse(
    """
    Log analyzer with date/time filtering
    
    Examples:
        $ analyze --start-date 2024-01-01 --end-date 2024-12-31 --time 14:30:00
        $ analyze --from "Jan 1, 2024" --to "Dec 31, 2024" --at "2:30 PM"
        $ analyze start:2024-01-01T09:00:00 end:2024-01-31T17:00:00
        $ analyze --since yesterday --until tomorrow --hour 15
    """
)

print("The LLM understands various date/time formats:")
print("  - ISO format: 2024-01-01")
print("  - Human readable: 'Jan 1, 2024'")
print("  - Relative: yesterday, tomorrow")
print("  - Times: 14:30:00, '2:30 PM'")
print()

# Example 6: Ranges and constraints
print("=" * 50)
print("Example 6: Ranges and Constraints")
print("=" * 50)

args = autocli.parse(
    """
    Server configuration with value ranges
    
    Examples:
        $ server --port 8080 --workers 4 --timeout 30.5 --memory 2GB
        $ server --port-range 8000-9000 --worker-threads 1-16 --timeout 10.0-60.0
        $ server port:3000 workers:8 timeout:45.5 memory:512MB
        
    Note: Port must be 1-65535, workers 1-100, timeout 0.1-300.0 seconds
    """
)

print("The LLM can understand:")
print("  - Single values: port 8080")
print("  - Ranges: port-range 8000-9000")
print("  - Units: memory 2GB, 512MB")
print("  - Constraints from context")

print("\n" + "=" * 50)
print("All these different formats are understood by the LLM!")
print("It infers types from context and examples automatically.")
print("=" * 50)