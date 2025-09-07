"""
Pydantic RPN - A delightful Python library for Reverse Polish Notation

This library provides an intuitive, type-safe way to work with RPN expressions
with full Pydantic integration for validation and serialization.
"""

from .core import RPN, rpn, RPNError, ValidationError, EvaluationError, RPNBuilder
from .config import Config
from .repl import REPL

__version__ = "0.1.0"
__all__ = ["RPN", "rpn", "RPNError", "ValidationError", "EvaluationError", "RPNBuilder", "Config", "REPL"]