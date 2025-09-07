"""Interactive REPL for RPN expressions."""

import sys
from typing import Dict, Any, Optional
from .core import RPN, RPNError


class REPL:
    """Interactive RPN calculator with REPL interface."""
    
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.last_result: Optional[Any] = None
    
    def run(self):
        """Start the interactive REPL."""
        print("Pydantic RPN Calculator")
        print("Type 'help' for commands, 'exit' to quit")
        print()
        
        while True:
            try:
                user_input = input("rpn> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ('exit', 'quit'):
                    break
                
                if user_input.lower() == 'help':
                    self._show_help()
                    continue
                
                if user_input.lower() == 'vars':
                    self._show_variables()
                    continue
                
                if user_input.lower() == 'clear':
                    self.variables.clear()
                    self.last_result = None
                    print("Variables and history cleared")
                    continue
                
                result = self.execute(user_input)
                if result is not None:
                    print(result)
                
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
                continue
            except EOFError:
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def execute(self, expression: str) -> Any:
        """
        Execute a single RPN expression or command.
        
        Args:
            expression: RPN expression or variable assignment
            
        Returns:
            Result of the expression
        """
        # Handle variable assignments: x = 10
        if '=' in expression and not any(op in expression for op in ['==', '!=', '<=', '>=']):
            parts = expression.split('=', 1)
            if len(parts) == 2:
                var_name = parts[0].strip()
                var_expr = parts[1].strip()
                
                if var_expr:
                    # Evaluate the right side
                    result = self._evaluate_expression(var_expr)
                    self.variables[var_name] = result
                    print(f"{var_name} = {result}")
                    return None
        
        # Regular expression evaluation
        result = self._evaluate_expression(expression)
        self.last_result = result
        self.variables['ans'] = result
        return result
    
    def _evaluate_expression(self, expression: str) -> Any:
        """Evaluate an RPN expression with current context."""
        try:
            rpn = RPN(expression, strict=False)
            return rpn.eval(**self.variables)
        except RPNError as e:
            raise e
        except Exception as e:
            raise RPNError(f"Evaluation failed: {e}") from e
    
    def _show_help(self):
        """Show help information."""
        print("""
Available commands:
  help          - Show this help
  vars          - Show all variables
  clear         - Clear variables and history
  exit, quit    - Exit the calculator

Variable assignment:
  x = 10        - Assign value to variable
  ans           - Last result (automatically set)

RPN Operations:
  3 4 +         - Addition: 7
  10 3 -        - Subtraction: 7
  5 2 *         - Multiplication: 10
  15 3 /        - Division: 5
  2 3 **        - Power: 8
  25 sqrt       - Square root: 5
  3.14159 sin   - Sine: ~0
  x dup *       - Square x (using stack ops)

Stack operations:
  dup           - Duplicate top item
  swap          - Swap top two items
  drop          - Remove top item
  rot           - Rotate top three items
  over          - Copy second item to top
        """)
    
    def _show_variables(self):
        """Show all current variables."""
        if not self.variables:
            print("No variables defined")
        else:
            print("Variables:")
            for name, value in self.variables.items():
                print(f"  {name} = {value}")
        
        if self.last_result is not None:
            print(f"  ans = {self.last_result} (last result)")