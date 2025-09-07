# autocli

Parse CLI arguments from natural language descriptions using small LLMs.

## Features

- Natural language CLI description parsing
- Automatic argument type inference
- Support for positional and named arguments
- Built-in help generation
- Small, efficient LLM (Flan-T5-small, ~250MB)
- Fallback regex parser for reliability
- Returns arguments as NamedTuple-like objects

## Installation

```bash
pip install autocli
```

## Quick Start

```python
import autocli

args = autocli.parse(
    """
    This app greets someone with excitement
    
        $ python greet.py --name Alice --excitement 3
        Hello, Alice!!!
    """
)

print(f"Hello, {args.name}{'!' * args.excitement}")
```

## Examples

### Positional args

```python
import autocli

args = autocli.parse(
    """
    This app adds two numbers and prints their sum

        $ python sum.py 1 2
        3
    """
)

print(args[0] + args[1])
```

### Named args and defaults

```python
import autocli

args = autocli.parse(
    """
    This app prints the file with the longest name in the given directory (default: PWD)

        $ ls /tmp
        a.txt ab.txt abc.txt

        $ python longest_filename.py --path /tmp
        abc.txt
    """
)

print(f'finding the longest filename in directory: {args.path})
```

### Named args wth numeric values and allowed ranges

```python
# greet.py

import autocli

args = autocli.parse(
    """
    This app greets the given `name` defaulting to "Earthling" and
    appends `excitement` number of exclamation marks.
    """
)

print(f'{args.name}{'!' * args.excitement}')
```

```
$ python greet.py --help
Greets the given name.

Options:

    -n NAME
    --name NAME

        NAME is who is being greeted.

        Default: "Earthling"

    -e EXCITEMENT
    --excitement EXCITEMENT

        EXCITEMENT is a positive integer that contols
        the number of exclamation marks.

        Default: 1
```

```
$ python greet.py -e -3
ERROR: The value for EXCITEMENT is too low. The lowest value is 1,
which is also the default.

    -e EXCITEMENT
    --excitement EXCITEMENT

        EXCITEMENT is a positive integer that contols
        the number of exclamation marks.

        Default: 1

Did you mean?
    python greet.py -e 3
```

```
$ python greet.py --excitement 42
Greetings, Earthling!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
```

## How It Works

1. **LLM Parsing**: Uses Google's Flan-T5-small model to understand your CLI description
2. **Structured Output**: Converts natural language to structured argument specifications
3. **Automatic ArgParse**: Generates standard Python argparse configuration
4. **NamedTuple-like Access**: Returns arguments as an object supporting both attribute and index access

## Advanced Usage

### Custom Model

```python
from autocli.parser import LLMParser

# Use a different model
parser = LLMParser(model_name="google/flan-t5-base")
```

### Accessing Arguments

```python
args = autocli.parse(description)

# Named arguments via attributes
print(args.name)
print(args.port)

# Positional arguments via indexing
print(args[0])  # First positional arg
print(args[1])  # Second positional arg
```

## Requirements

- Python 3.8+
- PyTorch 2.0+
- Transformers 4.30+

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
