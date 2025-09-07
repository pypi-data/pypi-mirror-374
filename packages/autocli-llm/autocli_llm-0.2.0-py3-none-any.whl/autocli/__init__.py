"""
autocli - Parse CLI arguments from natural language using LLMs
"""

from .parser import parse, AutoCLIArgs

__version__ = "0.2.0"
__all__ = ["parse", "AutoCLIArgs"]