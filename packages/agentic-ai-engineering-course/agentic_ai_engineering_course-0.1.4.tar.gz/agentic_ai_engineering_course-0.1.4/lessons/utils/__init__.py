"""
Course AI Agents Utils

A collection of utility functions for AI agents development.
"""

__version__ = "0.1.0"

from .env import load
from .pretty_print import wrapped, function_call, Color

__all__ = ["load", "wrapped", "function_call", "Color"]
