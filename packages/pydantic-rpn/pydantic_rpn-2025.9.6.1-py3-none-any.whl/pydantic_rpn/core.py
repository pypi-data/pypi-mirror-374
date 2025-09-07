"""Core RPN implementation with delightful developer experience."""

import json
import math
import operator
import re
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from pydantic import BaseModel, Field, validator
from pydantic.types import StrictFloat, StrictInt


class RPNError(Exception):
    """Base exception for RPN-related errors."""
    pass


class ValidationError(RPNError):
    """Raised when RPN expression validation fails."""
    pass


class EvaluationError(RPNError):
    """Raised when RPN expression evaluation fails."""
    pass


class RPN(BaseModel):
    """
    A delightful RPN (Reverse Polish Notation) expression with Pydantic integration.
    
    Examples:
        >>> expr = RPN("3 4 +")
        >>> expr.eval()  # 7
        >>> expr = RPN([3, 4, "+"])
        >>> expr()  # 7 (shorthand for eval)
        >>> rpn("3 4 +").eval()  # 7 (convenience function)
    """
    
    tokens: List[Union[str, int, float]] = Field(description="RPN expression tokens")
    defaults: Dict[str, Union[int, float]] = Field(default_factory=dict, description="Default variable values")
    strict: bool = Field(default=False, description="Whether to validate expression on creation")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Optional metadata")
    
    # Built-in operators
    _operators = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
        '//': operator.floordiv,
        '%': operator.mod,
        '**': operator.pow,
        'pow': operator.pow,
        '==': operator.eq,
        '!=': operator.ne,
        '<': operator.lt,
        '>': operator.gt,
        '<=': operator.le,
        '>=': operator.ge,
        'and': operator.and_,
        'or': operator.or_,
        'not': operator.not_,
        'abs': abs,
        'neg': operator.neg,
        'sqrt': math.sqrt,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'log': math.log10,
        'ln': math.log,
        'exp': math.exp,
        'ceil': math.ceil,
        'floor': math.floor,
        'round': round,
        'max': max,
        'min': min,
    }
    
    # Stack operations - these should fail if insufficient items
    _stack_ops = {
        'dup': lambda stack: stack + [stack[-1]] if len(stack) >= 1 else (_ for _ in ()).throw(EvaluationError("dup requires at least 1 item on stack")),
        'drop': lambda stack: stack[:-1] if len(stack) >= 1 else (_ for _ in ()).throw(EvaluationError("drop requires at least 1 item on stack")),
        'swap': lambda stack: stack[:-2] + [stack[-1], stack[-2]] if len(stack) >= 2 else (_ for _ in ()).throw(EvaluationError("swap requires at least 2 items on stack")),
        'rot': lambda stack: stack[:-3] + [stack[-2], stack[-1], stack[-3]] if len(stack) >= 3 else (_ for _ in ()).throw(EvaluationError("rot requires at least 3 items on stack")),
        'over': lambda stack: stack + [stack[-2]] if len(stack) >= 2 else (_ for _ in ()).throw(EvaluationError("over requires at least 2 items on stack")),
    }
    
    # Constants
    _constants = {
        'pi': math.pi,
        'e': math.e,
        'tau': math.tau,
        'inf': math.inf,
        'true': True,
        'false': False,
    }
    
    def __init__(self, expression=None, **kwargs):
        """
        Create an RPN expression.
        
        Args:
            expression: Can be a string "3 4 +", list [3, 4, "+"], or variadic args
            **kwargs: Additional parameters (defaults, strict, metadata)
        """
        if isinstance(expression, str):
            tokens = expression.split()
        elif isinstance(expression, list):
            tokens = expression
        elif expression is None:
            tokens = []
        else:
            # Handle variadic args: RPN(3, 4, "+")
            tokens = [expression] + list(kwargs.pop('_args', []))
            
        # Convert numeric strings to numbers
        processed_tokens = []
        for token in tokens:
            if isinstance(token, str):
                # Try to parse as number, but don't force it
                try:
                    if '.' in token:
                        processed_tokens.append(float(token))
                    elif token.lstrip('-').isdigit():  # Handle negative integers
                        processed_tokens.append(int(token))
                    else:
                        processed_tokens.append(token)  # Keep as string
                except ValueError:
                    processed_tokens.append(token)  # Keep as string if parsing fails
            else:
                processed_tokens.append(token)
        
        super().__init__(tokens=processed_tokens, **kwargs)
        
        if self.strict:
            self.validate_expression()
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod  
    def validate(cls, value):
        """Pydantic validator for RPN expressions."""
        if isinstance(value, cls):
            return value
        return cls(value)
    
    def validate_expression(self) -> List[str]:
        """
        Validate the RPN expression syntax.
        
        Returns:
            List of error messages (empty if valid)
            
        Raises:
            ValidationError: If expression is invalid and strict=True
        """
        errors = []
        stack_size = 0
        
        for i, token in enumerate(self.tokens):
            if self._is_operator(token):
                if str(token) in self._stack_ops:
                    # Handle stack operations specially
                    if str(token) in ['dup', 'over'] and stack_size < 1:
                        error = f"Token {i}: '{token}' requires at least 1 item on stack, but stack has {stack_size}"
                        errors.append(error)
                        if self.strict:
                            raise ValidationError(error)
                    elif str(token) in ['swap', 'rot'] and stack_size < 2:
                        error = f"Token {i}: '{token}' requires at least 2 items on stack, but stack has {stack_size}"
                        errors.append(error)
                        if self.strict:
                            raise ValidationError(error)
                    elif str(token) == 'drop' and stack_size < 1:
                        error = f"Token {i}: '{token}' requires at least 1 item on stack, but stack has {stack_size}"
                        errors.append(error)
                        if self.strict:
                            raise ValidationError(error)
                    
                    # Update stack size based on stack operation
                    if str(token) == 'dup':
                        stack_size += 1  # Duplicates top item
                    elif str(token) == 'drop':
                        stack_size -= 1  # Removes top item
                    elif str(token) == 'over':
                        stack_size += 1  # Copies second item to top
                    # swap and rot don't change stack size
                        
                else:
                    # Handle regular operators
                    required_operands = self._get_operator_arity(token)
                    if stack_size < required_operands:
                        error = f"Token {i}: '{token}' requires {required_operands} operands, but stack only has {stack_size}"
                        errors.append(error)
                        if self.strict:
                            raise ValidationError(error)
                    stack_size -= required_operands - 1  # Pop operands, push result
            else:
                # It's a number, variable, or constant - add to stack
                stack_size += 1
        
        # Only validate stack size if we're certain it's not due to unknown operators
        # Unknown operators will be caught during evaluation
        if stack_size != 1 and stack_size > 0:
            # Only enforce single result if all tokens are known
            if all(self._is_operator(token) or self._is_known_token(token) for token in self.tokens):
                error = f"Expression leaves {stack_size} items on stack, expected 1"
                errors.append(error)
                if self.strict:
                    raise ValidationError(error)
                
        return errors
    
    def _is_operator(self, token: Any) -> bool:
        """Check if token is an operator."""
        return str(token) in self._operators or str(token) in self._stack_ops
    
    def _is_known_token(self, token: Any) -> bool:
        """Check if token is a known constant or can be parsed as number."""
        token_str = str(token)
        return (token_str in self._constants or 
                self._is_number(token_str))
    
    def _is_number(self, token_str: str) -> bool:
        """Check if string can be parsed as a number."""
        try:
            # Try to parse as int first, then float
            if '.' in token_str or 'e' in token_str.lower():
                float(token_str)
            else:
                int(token_str)
            return True
        except ValueError:
            return False
    
    def _get_operator_arity(self, token: str) -> int:
        """Get the number of operands an operator requires (excludes stack operations)."""
        unary_ops = {'not', 'abs', 'neg', 'sqrt', 'sin', 'cos', 'tan', 'log', 'ln', 'exp', 'ceil', 'floor', 'round'}
        if token in unary_ops:
            return 1
        return 2
    
    def eval(self, **variables) -> Union[int, float, bool]:
        """
        Evaluate the RPN expression.
        
        Args:
            **variables: Variable substitutions
            
        Returns:
            Result of the expression
            
        Raises:
            EvaluationError: If evaluation fails
        """
        # Merge defaults with provided variables
        context = {**self.defaults, **variables}
        
        stack = []
        
        for token in self.tokens:
            try:
                if self._is_operator(token):
                    if str(token) in self._stack_ops:
                        stack = self._stack_ops[str(token)](stack)
                    else:
                        func = self._operators[str(token)]
                        arity = self._get_operator_arity(str(token))
                        
                        if len(stack) < arity:
                            raise EvaluationError(f"Insufficient operands for '{token}'")
                        
                        if arity == 1:
                            operand = stack.pop()
                            result = func(operand)
                        else:
                            right = stack.pop()
                            left = stack.pop()
                            result = func(left, right)
                        
                        stack.append(result)
                else:
                    # Handle variables, constants, and literals
                    value = self._resolve_token(token, context)
                    stack.append(value)
                    
            except Exception as e:
                raise EvaluationError(f"Error evaluating token '{token}': {str(e)}") from e
        
        if len(stack) == 0:
            # Empty expression returns True (or could return 0)
            return True
        elif len(stack) == 1:
            return stack[0]
        else:
            # HP calculator behavior: return top of stack if multiple items
            # This allows partial expressions and stack operations
            return stack[-1]
    
    def __call__(self, **variables) -> Union[int, float, bool]:
        """Make RPN objects directly callable - cleaner than .eval()"""
        return self.eval(**variables)
    
    def _resolve_token(self, token: Any, context: Dict[str, Any]) -> Union[int, float, bool]:
        """Resolve a token to its numeric value."""
        if isinstance(token, (int, float, bool)):
            return token
        
        token_str = str(token)
        
        # Check variables first (allows shadowing of constants)
        if token_str in context:
            return context[token_str]
        
        # Then check constants
        if token_str in self._constants:
            return self._constants[token_str]
        
        # Try to parse as number
        try:
            # Check if it looks like a float (contains ., e, or E for scientific notation)
            if '.' in token_str or 'e' in token_str.lower():
                return float(token_str)
            else:
                return int(token_str)
        except ValueError:
            raise EvaluationError(f"Unknown token: '{token}'")
    
    def __call__(self, **variables) -> Union[int, float, bool]:
        """Shorthand for eval()."""
        return self.eval(**variables)
    
    def __str__(self) -> str:
        """String representation of the RPN expression."""
        return ' '.join(str(token) for token in self.tokens)
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"RPN('{self}')"
    
    def __add__(self, other: 'RPN') -> 'RPN':
        """Combine two RPN expressions."""
        if isinstance(other, RPN):
            # Preserve non-strict mode if either expression is non-strict
            strict = self.strict and other.strict
            return RPN(self.tokens + other.tokens, 
                      defaults={**self.defaults, **other.defaults},
                      strict=strict,
                      metadata={**self.metadata, **other.metadata})
        return NotImplemented
    
    def __or__(self, other: 'RPN') -> Union[int, float, bool]:
        """Pipe operator: evaluate self, then use result as context for other."""
        result = self.eval()
        return other.eval(ans=result)
    
    # Method chaining operations
    def push(self, value: Union[int, float, str]) -> 'RPN':
        """Push a value onto the expression stack."""
        return RPN(self.tokens + [value], defaults=self.defaults, strict=self.strict)
    
    def add(self) -> 'RPN':
        """Add the + operator."""
        return RPN(self.tokens + ['+'], defaults=self.defaults, strict=self.strict)
    
    def sub(self) -> 'RPN':
        """Add the - operator."""
        return RPN(self.tokens + ['-'], defaults=self.defaults, strict=self.strict)
    
    def mul(self) -> 'RPN':
        """Add the * operator."""
        return RPN(self.tokens + ['*'], defaults=self.defaults, strict=self.strict)
    
    def div(self) -> 'RPN':
        """Add the / operator."""
        return RPN(self.tokens + ['/'], defaults=self.defaults, strict=self.strict)
    
    def pow(self) -> 'RPN':
        """Add the ** operator."""
        return RPN(self.tokens + ['**'], defaults=self.defaults, strict=self.strict)
    
    # Stack operations
    def dup(self) -> 'RPN':
        """Duplicate top stack item."""
        return RPN(self.tokens + ['dup'], defaults=self.defaults, strict=self.strict)
    
    def swap(self) -> 'RPN':
        """Swap top two stack items."""
        return RPN(self.tokens + ['swap'], defaults=self.defaults, strict=self.strict)
    
    def drop(self) -> 'RPN':
        """Drop top stack item."""
        return RPN(self.tokens + ['drop'], defaults=self.defaults, strict=self.strict)
    
    def rot(self) -> 'RPN':
        """Rotate top three stack items."""
        return RPN(self.tokens + ['rot'], defaults=self.defaults, strict=self.strict)
    
    def over(self) -> 'RPN':
        """Copy second item to top."""
        return RPN(self.tokens + ['over'], defaults=self.defaults, strict=self.strict)
    
    # Math functions
    def sqrt(self) -> 'RPN':
        """Add sqrt function."""
        return RPN(self.tokens + ['sqrt'], defaults=self.defaults, strict=self.strict)
    
    def sin(self) -> 'RPN':
        """Add sin function."""
        return RPN(self.tokens + ['sin'], defaults=self.defaults, strict=self.strict)
    
    def cos(self) -> 'RPN':
        """Add cos function."""
        return RPN(self.tokens + ['cos'], defaults=self.defaults, strict=self.strict)
    
    # Conversion methods
    def to_infix(self) -> str:
        """Convert RPN to infix notation (basic implementation)."""
        stack = []
        
        for token in self.tokens:
            if self._is_operator(token) and str(token) not in self._stack_ops:
                if str(token) in {'abs', 'sqrt', 'sin', 'cos', 'tan', 'log', 'ln', 'exp', 'ceil', 'floor', 'round', 'not', 'neg'}:
                    # Unary operator
                    if stack:
                        operand = stack.pop()
                        if token == 'neg':
                            result = f"(-{operand})"
                        else:
                            result = f"{token}({operand})"
                        stack.append(result)
                else:
                    # Binary operator
                    if len(stack) >= 2:
                        right = stack.pop()
                        left = stack.pop()
                        result = f"({left} {token} {right})"
                        stack.append(result)
            else:
                stack.append(str(token))
        
        return stack[0] if stack else ""
    
    def to_prefix(self) -> str:
        """Convert RPN to prefix notation (basic implementation)."""
        # This is a simplified implementation
        # A full implementation would require more sophisticated parsing
        return f"prefix({' '.join(str(t) for t in self.tokens)})"
    
    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps({
            'tokens': self.tokens,
            'defaults': self.defaults,
            'metadata': self.metadata
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> 'RPN':
        """Deserialize from JSON."""
        data = json.loads(json_str)
        return cls(
            expression=data['tokens'],
            defaults=data.get('defaults', {}),
            metadata=data.get('metadata', {})
        )
    
    # Template and partial evaluation
    @classmethod
    def template(cls, template_str: str) -> 'RPN':
        """Create a template RPN with ${variable} placeholders."""
        # Replace ${var} with var for now - could be more sophisticated
        processed = re.sub(r'\$\{(\w+)\}', r'\1', template_str)
        return cls(processed)
    
    def partial(self, **values) -> 'RPN':
        """Create a new RPN with some variables pre-evaluated."""
        new_defaults = {**self.defaults, **values}
        return RPN(self.tokens, defaults=new_defaults, strict=self.strict, metadata=self.metadata)


class RPNBuilder:
    """Fluent interface for building RPN expressions."""
    
    def __init__(self):
        self.tokens = []
    
    def push(self, value: Union[int, float, str]) -> 'RPNBuilder':
        """Push a value."""
        self.tokens.append(value)
        return self
    
    def var(self, name: str) -> 'RPNBuilder':
        """Push a variable."""
        self.tokens.append(name)
        return self
    
    def add(self) -> 'RPNBuilder':
        """Add addition operator."""
        self.tokens.append('+')
        return self
    
    def sub(self) -> 'RPNBuilder':
        """Add subtraction operator."""
        self.tokens.append('-')
        return self
    
    def mul(self) -> 'RPNBuilder':
        """Add multiplication operator."""
        self.tokens.append('*')
        return self
    
    def div(self) -> 'RPNBuilder':
        """Add division operator."""
        self.tokens.append('/')
        return self
    
    def pow(self) -> 'RPNBuilder':
        """Add power operator."""
        self.tokens.append('**')
        return self
    
    def neg(self) -> 'RPNBuilder':
        """Add negation operator."""
        self.tokens.append('neg')
        return self
    
    def sqrt(self) -> 'RPNBuilder':
        """Add square root function."""
        self.tokens.append('sqrt')
        return self
    
    # Stack operations
    def dup(self) -> 'RPNBuilder':
        """Add dup stack operation."""
        self.tokens.append('dup')
        return self
    
    def swap(self) -> 'RPNBuilder':
        """Add swap stack operation."""
        self.tokens.append('swap')
        return self
    
    def drop(self) -> 'RPNBuilder':
        """Add drop stack operation."""
        self.tokens.append('drop')
        return self
    
    def rot(self) -> 'RPNBuilder':
        """Add rot stack operation."""
        self.tokens.append('rot')
        return self
    
    def over(self) -> 'RPNBuilder':
        """Add over stack operation."""
        self.tokens.append('over')
        return self
    
    # Math functions
    def abs(self) -> 'RPNBuilder':
        """Add absolute value function."""
        self.tokens.append('abs')
        return self
    
    def sin(self) -> 'RPNBuilder':
        """Add sine function."""
        self.tokens.append('sin')
        return self
    
    def cos(self) -> 'RPNBuilder':
        """Add cosine function."""
        self.tokens.append('cos')
        return self
    
    def tan(self) -> 'RPNBuilder':
        """Add tangent function."""
        self.tokens.append('tan')
        return self
    
    def log(self) -> 'RPNBuilder':
        """Add log10 function."""
        self.tokens.append('log')
        return self
    
    def ln(self) -> 'RPNBuilder':
        """Add natural log function."""
        self.tokens.append('ln')
        return self
    
    def exp(self) -> 'RPNBuilder':
        """Add exponential function."""
        self.tokens.append('exp')
        return self
    
    def build(self) -> RPN:
        """Build the final RPN expression."""
        return RPN(self.tokens)
    
    def eval(self, **variables) -> Union[int, float, bool]:
        """Build and evaluate in one step."""
        return self.build().eval(**variables)
    
    def __call__(self, **variables) -> Union[int, float, bool]:
        """Make RPNBuilder directly callable - cleaner than .eval()"""
        return self.eval(**variables)


# Enhanced RPN expression class with operator overloading
class RPNExpr:
    """
    Pythonic RPN expressions with operator overloading.
    
    Used internally by rpn() function. Supports auto-wrapping of numbers:
        rpn(3) + 4 * 2  # Only need rpn() once - numbers auto-wrap
    """
    
    def __init__(self, value: Union[str, List, int, float]):
        if isinstance(value, (int, float)):
            # Single number
            self._rpn = RPN([value])
        elif isinstance(value, str):
            if ' ' in value:
                # Multi-token expression like "3 4 +"
                self._rpn = RPN(value)
            else:
                # Single variable or number token
                self._rpn = RPN([value])
        elif isinstance(value, list):
            # Token list
            self._rpn = RPN(value)
        else:
            raise TypeError(f"Cannot create RPNExpr from {type(value)}")
    
    def _ensure_rpn_expr(self, other) -> 'RPNExpr':
        """Convert numbers and RPN objects to RPNExpr objects automatically"""
        if isinstance(other, RPNExpr):
            return other
        elif isinstance(other, (int, float, str)):
            return RPNExpr(other)
        elif isinstance(other, RPN):
            result = RPNExpr(0)
            result._rpn = other
            return result
        else:
            raise TypeError(f"Cannot convert {type(other)} to RPNExpr object")
    
    def __add__(self, other) -> 'RPNExpr':
        other_v = self._ensure_rpn_expr(other)
        result = RPNExpr(0)  # Dummy value, will be replaced
        result._rpn = self._rpn + other_v._rpn + RPN(['+'])
        return result
    
    def __radd__(self, other) -> 'RPNExpr':
        """Support 3 + RPNExpr(4) syntax"""
        other_v = self._ensure_rpn_expr(other)
        result = RPNExpr(0)
        result._rpn = other_v._rpn + self._rpn + RPN(['+'])
        return result
    
    def __sub__(self, other) -> 'RPNExpr':
        other_v = self._ensure_rpn_expr(other)
        result = RPNExpr(0)
        result._rpn = self._rpn + other_v._rpn + RPN(['-'])
        return result
    
    def __rsub__(self, other) -> 'RPNExpr':
        """Support 10 - V(3) syntax"""
        other_v = self._ensure_rpn_expr(other)
        result = RPNExpr(0)
        result._rpn = other_v._rpn + self._rpn + RPN(['-'])
        return result
    
    def __mul__(self, other) -> 'RPNExpr':
        other_v = self._ensure_rpn_expr(other)
        result = RPNExpr(0)
        result._rpn = self._rpn + other_v._rpn + RPN(['*'])
        return result
    
    def __rmul__(self, other) -> 'RPNExpr':
        """Support 5 * V(2) syntax"""
        other_v = self._ensure_rpn_expr(other)
        result = RPNExpr(0)
        result._rpn = other_v._rpn + self._rpn + RPN(['*'])
        return result
    
    def __truediv__(self, other) -> 'RPNExpr':
        other_v = self._ensure_rpn_expr(other)
        result = RPNExpr(0)
        result._rpn = self._rpn + other_v._rpn + RPN(['/'])
        return result
    
    def __rtruediv__(self, other) -> 'RPNExpr':
        """Support 100 / V(5) syntax"""
        other_v = self._ensure_rpn_expr(other)
        result = RPNExpr(0)
        result._rpn = other_v._rpn + self._rpn + RPN(['/'])
        return result
    
    def __pow__(self, other) -> 'RPNExpr':
        other_v = self._ensure_rpn_expr(other)
        result = RPNExpr(0)
        result._rpn = self._rpn + other_v._rpn + RPN(['**'])
        return result
    
    def __rpow__(self, other) -> 'RPNExpr':
        """Support 2 ** V(3) syntax"""
        other_v = self._ensure_rpn_expr(other)
        result = RPNExpr(0)
        result._rpn = other_v._rpn + self._rpn + RPN(['**'])
        return result
    
    def __floordiv__(self, other) -> 'RPNExpr':
        other_v = self._ensure_rpn_expr(other)
        result = RPNExpr(0)
        result._rpn = self._rpn + other_v._rpn + RPN(['//'])
        return result
    
    def __rfloordiv__(self, other) -> 'RPNExpr':
        """Support 17 // V(5) syntax"""
        other_v = self._ensure_rpn_expr(other)
        result = RPNExpr(0)
        result._rpn = other_v._rpn + self._rpn + RPN(['//'])
        return result
    
    def __mod__(self, other) -> 'RPNExpr':
        other_v = self._ensure_rpn_expr(other)
        result = RPNExpr(0)
        result._rpn = self._rpn + other_v._rpn + RPN(['%'])
        return result
    
    def __rmod__(self, other) -> 'RPNExpr':
        """Support 17 % V(5) syntax"""
        other_v = self._ensure_rpn_expr(other)
        result = RPNExpr(0)
        result._rpn = other_v._rpn + self._rpn + RPN(['%'])
        return result
    
    # Comparison operators with auto-wrapping
    def __eq__(self, other) -> 'RPNExpr':
        other_v = self._ensure_rpn_expr(other)
        result = RPNExpr(0)
        result._rpn = self._rpn + other_v._rpn + RPN(['=='])
        return result
    
    def __lt__(self, other) -> 'RPNExpr':
        other_v = self._ensure_rpn_expr(other)
        result = RPNExpr(0)
        result._rpn = self._rpn + other_v._rpn + RPN(['<'])
        return result
    
    def __le__(self, other) -> 'RPNExpr':
        other_v = self._ensure_rpn_expr(other)
        result = RPNExpr(0)
        result._rpn = self._rpn + other_v._rpn + RPN(['<='])
        return result
    
    def __gt__(self, other) -> 'RPNExpr':
        other_v = self._ensure_rpn_expr(other)
        result = RPNExpr(0)
        result._rpn = self._rpn + other_v._rpn + RPN(['>'])
        return result
    
    def __ge__(self, other) -> 'RPNExpr':
        other_v = self._ensure_rpn_expr(other)
        result = RPNExpr(0)
        result._rpn = self._rpn + other_v._rpn + RPN(['>='])
        return result
    
    def __ne__(self, other) -> 'RPNExpr':
        other_v = self._ensure_rpn_expr(other)
        result = RPNExpr(0)
        result._rpn = self._rpn + other_v._rpn + RPN(['!='])
        return result
    
    # Unary operations as methods
    def sqrt(self) -> 'RPNExpr':
        result = RPNExpr(0)
        result._rpn = self._rpn + RPN(['sqrt'])
        return result
    
    def abs(self) -> 'RPNExpr':
        result = RPNExpr(0)
        result._rpn = self._rpn + RPN(['abs'])
        return result
    
    def neg(self) -> 'RPNExpr':
        result = RPNExpr(0)
        result._rpn = self._rpn + RPN(['neg'])
        return result
    
    def sin(self) -> 'RPNExpr':
        result = RPNExpr(0)
        result._rpn = self._rpn + RPN(['sin'])
        return result
    
    def cos(self) -> 'RPNExpr':
        result = RPNExpr(0)
        result._rpn = self._rpn + RPN(['cos'])
        return result
    
    def tan(self) -> 'RPNExpr':
        result = RPNExpr(0)
        result._rpn = self._rpn + RPN(['tan'])
        return result
    
    def log(self) -> 'RPNExpr':
        result = RPNExpr(0)
        result._rpn = self._rpn + RPN(['log'])
        return result
    
    def ln(self) -> 'RPNExpr':
        result = RPNExpr(0)
        result._rpn = self._rpn + RPN(['ln'])
        return result
    
    def exp(self) -> 'RPNExpr':
        result = RPNExpr(0)
        result._rpn = self._rpn + RPN(['exp'])
        return result
    
    # Stack operations
    def dup(self) -> 'RPNExpr':
        result = RPNExpr(0)
        result._rpn = self._rpn + RPN(['dup'])
        return result
    
    def swap(self, other) -> 'RPNExpr':
        """Swap with another value"""
        other_v = self._ensure_rpn_expr(other)
        result = RPNExpr(0)
        result._rpn = self._rpn + other_v._rpn + RPN(['swap'])
        return result
    
    # Evaluation and conversion methods
    def __call__(self, **variables) -> Union[int, float, bool]:
        """Make V objects directly callable"""
        return self._rpn(**variables)
    
    def eval(self, **variables) -> Union[int, float, bool]:
        """Evaluate the expression"""
        return self._rpn.eval(**variables)
    
    def to_rpn(self) -> RPN:
        """Convert to RPN object"""
        return self._rpn
    
    def to_string(self) -> str:
        """Get the RPN expression as a string"""
        return ' '.join(str(token) for token in self._rpn.tokens)
    
    def __str__(self) -> str:
        return f"rpn({self.to_string()})"
    
    def __repr__(self) -> str:
        return f"rpn({self.to_string()})"


# Simple, clean rpn function that supports operators
def rpn(value: Union[str, List, int, float]) -> 'RPNExpr':
    """
    The ONE way to create RPN expressions - clean and pythonic.
    
    Examples:
        # Clean operator syntax - the best way!
        result = rpn(3) + 4 * 2        # Auto-wrapping: only need rpn() once
        formula = rpn('revenue') - 800 * 0.1  # Variables work perfectly
        
        # Traditional syntax still works if you prefer  
        result = rpn("3 4 + 2 *")()    # Same result
        
        # Call directly to evaluate
        print(result())                # 14
        print(formula(revenue=1000))   # 920.0
    """
    return RPNExpr(value)