import sys
import json
import re
from typing import Any, Dict, List, Optional, NamedTuple
from collections import namedtuple
import argparse

from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch


class AutoCLIArgs:
    """Dynamic argument container that supports both attribute and index access."""
    
    def __init__(self, args_dict: Dict[str, Any], positional_args: List[Any] = None):
        self._args = args_dict
        self._positional = positional_args or []
        
        for key, value in args_dict.items():
            setattr(self, key, value)
    
    def __getitem__(self, key):
        if isinstance(key, int):
            return self._positional[key]
        return self._args[key]
    
    def __repr__(self):
        return f"AutoCLIArgs({self._args})"


class LLMParser:
    """Handles LLM-based parsing of CLI descriptions."""
    
    def __init__(self, model_name: str = "google/flan-t5-small"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name).to(self.device)
        self.model.eval()
    
    def create_prompt(self, description: str) -> str:
        """Create a prompt for the LLM to parse CLI arguments."""
        prompt = f"""Parse the following CLI application description and extract the arguments.
Return a JSON object with these fields:
- "positional": list of positional argument names
- "named": dict of named arguments with their properties (type, default, required, short_flag, long_flag)
- "description": brief app description

CLI Description:
{description}

Output the arguments as JSON:"""
        return prompt
    
    def parse_description(self, description: str) -> Dict[str, Any]:
        """Parse CLI description using the LLM."""
        try:
            prompt = self.create_prompt(description)
            
            inputs = self.tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=256,
                    num_beams=4,
                    temperature=0.1,
                    do_sample=False
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            try:
                parsed = json.loads(response)
            except json.JSONDecodeError:
                parsed = self._fallback_parse(description)
        except Exception:
            # If LLM fails for any reason, use fallback parser
            parsed = self._fallback_parse(description)
        
        return parsed
    
    def _fallback_parse(self, description: str) -> Dict[str, Any]:
        """Fallback parser using regex when LLM fails."""
        result = {
            "positional": [],
            "named": {},
            "description": ""
        }
        
        lines = description.strip().split('\n')
        result["description"] = lines[0] if lines else ""
        
        example_pattern = r'\$\s*python\s+\S+\.py\s+(.*)'
        flag_pattern = r'--?(\w+)(?:\s+(\w+))?'
        
        for line in lines:
            example_match = re.search(example_pattern, line)
            if example_match:
                args_str = example_match.group(1)
                
                flags = re.findall(flag_pattern, args_str)
                for flag, value in flags:
                    if flag not in result["named"]:
                        result["named"][flag] = {
                            "type": "str",
                            "default": None,
                            "required": False,
                            "long_flag": f"--{flag}",
                            "short_flag": f"-{flag[0]}" if len(flag) > 1 else None
                        }
                
                remaining = re.sub(flag_pattern, '', args_str).strip()
                if remaining:
                    positionals = remaining.split()
                    for pos in positionals:
                        if not pos.startswith('-') and pos not in result["positional"]:
                            result["positional"].append(f"arg{len(result['positional'])}")
        
        return result


def parse(description: str, argv: Optional[List[str]] = None) -> AutoCLIArgs:
    """
    Parse command-line arguments based on a natural language description.
    
    Args:
        description: Natural language description of the CLI app with examples
        argv: Optional list of arguments to parse (defaults to sys.argv[1:])
    
    Returns:
        AutoCLIArgs object containing parsed arguments
    """
    if argv is None:
        argv = sys.argv[1:]
    
    llm_parser = LLMParser()
    parsed_spec = llm_parser.parse_description(description)
    
    parser = argparse.ArgumentParser(
        description=parsed_spec.get("description", ""),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    positional_values = []
    named_args = {}
    
    for i, pos_arg in enumerate(parsed_spec.get("positional", [])):
        parser.add_argument(
            f"pos_{i}",
            metavar=pos_arg.upper(),
            help=f"Positional argument {i+1}"
        )
    
    for arg_name, arg_spec in parsed_spec.get("named", {}).items():
        flags = []
        if arg_spec.get("short_flag"):
            # Avoid -h conflict with help
            if arg_spec["short_flag"] != "-h":
                flags.append(arg_spec["short_flag"])
        if arg_spec.get("long_flag"):
            flags.append(arg_spec["long_flag"])
        
        if not flags:
            flags = [f"--{arg_name}"]
        
        arg_type = arg_spec.get("type", "str")
        type_func = {
            "int": int,
            "float": float,
            "bool": lambda x: x.lower() in ('true', '1', 'yes'),
            "str": str
        }.get(arg_type, str)
        
        parser.add_argument(
            *flags,
            dest=arg_name,
            type=type_func,
            default=arg_spec.get("default"),
            required=arg_spec.get("required", False),
            help=f"{arg_name.upper()} argument"
        )
    
    args = parser.parse_args(argv)
    
    for i in range(len(parsed_spec.get("positional", []))):
        positional_values.append(getattr(args, f"pos_{i}"))
    
    for arg_name in parsed_spec.get("named", {}):
        if hasattr(args, arg_name):
            named_args[arg_name] = getattr(args, arg_name)
    
    try:
        for pos_value in positional_values:
            if pos_value.replace('.', '').replace('-', '').isdigit():
                if '.' in pos_value:
                    positional_values[positional_values.index(pos_value)] = float(pos_value)
                else:
                    positional_values[positional_values.index(pos_value)] = int(pos_value)
    except:
        pass
    
    return AutoCLIArgs(named_args, positional_values)