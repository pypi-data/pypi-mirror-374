"""Command-line interface for pydantic-rpn."""

import argparse
import sys
from .core import RPN, RPNError
from .repl import REPL


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Pydantic RPN Calculator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  rpn "3 4 +"              # Evaluate expression: 7
  rpn --repl               # Start interactive calculator
  rpn "x 2 *" --var x=5    # Use variables: 10
  rpn "3 4 +" --infix      # Show infix: (3 + 4)
        """
    )
    
    parser.add_argument(
        'expression',
        nargs='?',
        help='RPN expression to evaluate'
    )
    
    parser.add_argument(
        '--repl',
        action='store_true',
        help='Start interactive REPL mode'
    )
    
    parser.add_argument(
        '--var',
        action='append',
        help='Define variables (format: name=value)'
    )
    
    parser.add_argument(
        '--infix',
        action='store_true',
        help='Show infix notation'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Only validate expression, don\'t evaluate'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output result as JSON'
    )
    
    args = parser.parse_args()
    
    if args.repl:
        repl = REPL()
        repl.run()
        return
    
    if not args.expression:
        parser.print_help()
        return
    
    try:
        # Parse variables
        variables = {}
        if args.var:
            for var_def in args.var:
                if '=' not in var_def:
                    print(f"Error: Invalid variable definition '{var_def}'. Use format: name=value")
                    sys.exit(1)
                name, value = var_def.split('=', 1)
                try:
                    variables[name.strip()] = float(value) if '.' in value else int(value)
                except ValueError:
                    variables[name.strip()] = value.strip()
        
        # Create RPN expression
        rpn = RPN(args.expression)
        
        if args.validate:
            errors = rpn.validate_expression()
            if errors:
                print("Validation errors:")
                for error in errors:
                    print(f"  {error}")
                sys.exit(1)
            else:
                print("Expression is valid")
                return
        
        if args.infix:
            print(rpn.to_infix())
            return
        
        # Evaluate expression
        result = rpn.eval(**variables)
        
        if args.json:
            import json
            print(json.dumps({"result": result, "expression": str(rpn)}))
        else:
            print(result)
    
    except RPNError as e:
        print(f"RPN Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()