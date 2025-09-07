#!/usr/bin/env python3
"""Basic usage examples for pydantic-rpn."""

from pydantic_rpn import RPN, rpn, RPNBuilder

def basic_arithmetic():
    """Demonstrate basic arithmetic operations."""
    print("=== Basic Arithmetic ===")
    
    # Different ways to create expressions
    print(f"String: RPN('3 4 +').eval() = {RPN('3 4 +').eval()}")
    print(f"List: RPN([3, 4, '+']).eval() = {RPN([3, 4, '+']).eval()}")
    print(f"Shorthand: rpn('3 4 +')() = {rpn('3 4 +')()}")
    
    # More operations
    operations = [
        ("Addition", "10 5 +"),
        ("Subtraction", "10 5 -"), 
        ("Multiplication", "10 5 *"),
        ("Division", "10 5 /"),
        ("Power", "2 3 **"),
        ("Square Root", "25 sqrt"),
    ]
    
    for name, expr in operations:
        result = rpn(expr).eval()
        print(f"{name}: {expr} = {result}")


def expression_composition():
    """Demonstrate expression composition."""
    print("\n=== Expression Composition ===")
    
    # Pipe operation
    expr1 = RPN("3 4 +")  # Valid: 7
    expr2 = RPN("ans 2 *")  # Uses result from first expression
    result = expr1 | expr2  # Pipe: 7 * 2 = 14
    print(f"Pipe operation: ({expr1}) | ({expr2}) = {result}")
    
    # Direct evaluation of complex expressions
    complex_expr = RPN("5 dup + 3 /")  # (5 + 5) / 3
    print(f"Complex: {complex_expr} = {complex_expr.eval()}")


def variables_and_templates():
    """Demonstrate variables and templates."""
    print("\n=== Variables and Templates ===")
    
    # Basic variables
    expr = RPN("x y +")
    print(f"Variables: {expr} with x=10, y=5 = {expr.eval(x=10, y=5)}")
    
    # With defaults
    expr_with_defaults = RPN("x y +", defaults={"x": 100})
    print(f"Defaults: {expr_with_defaults} with y=5 = {expr_with_defaults.eval(y=5)}")
    
    # Template
    template = RPN.template("${price} ${tax} + ${discount} -")
    result = template.eval(price=100, tax=10, discount=5)
    print(f"Template: price + tax - discount = {result}")
    
    # Partial evaluation
    expr = RPN("x 2 * y +")
    partial = expr.partial(x=5)  # Fix x=5
    print(f"Partial: x*2 + y with x=5, y=3 = {partial.eval(y=3)}")


def stack_operations():
    """Demonstrate stack operations."""
    print("\n=== Stack Operations ===")
    
    operations = [
        ("Duplicate", "5 dup +", "5 + 5"),
        ("Swap", "3 4 swap -", "4 - 3"),
        ("Drop", "3 4 5 drop +", "3 + 4"),
        ("Over", "3 4 over + +", "3 + 4 + 3"),
    ]
    
    for name, expr, desc in operations:
        result = rpn(expr).eval()
        print(f"{name}: {expr} ({desc}) = {result}")


def builder_pattern():
    """Demonstrate the builder pattern."""
    print("\n=== Builder Pattern ===")
    
    # Simple builder
    result = (RPNBuilder()
             .push(10)
             .push(20)
             .add()
             .push(2)
             .div()
             .eval())
    print(f"Builder: (10 + 20) / 2 = {result}")
    
    # Builder with variables
    expr = (RPNBuilder()
           .var("radius")
           .push(2)
           .pow()     # r²
           .var("pi")
           .mul()     # π * r²
           .build())
    
    import math
    area = expr.eval(radius=5, pi=math.pi)
    print(f"Circle area: π * r² with r=5 = {area:.2f}")



def validation_and_errors():
    """Demonstrate validation and error handling."""
    print("\n=== Validation and Error Handling ===")
    
    # Valid expression
    expr = RPN("3 4 +")
    errors = expr.validate_expression()
    print(f"Valid: {expr} - errors: {errors}")
    
    # Invalid expression (but we'll catch it)
    try:
        expr = RPN("3 +", strict=True)
    except Exception as e:
        print(f"Invalid: '3 +' - {type(e).__name__}: {e}")
    
    # Non-strict validation
    expr = RPN("3 +", strict=False)
    errors = expr.validate_expression()
    print(f"Non-strict: '3 +' - errors: {errors}")


def serialization():
    """Demonstrate serialization."""
    print("\n=== Serialization ===")
    
    # JSON serialization
    expr = RPN("3 4 + 2 *", metadata={"author": "demo", "purpose": "example"})
    json_str = expr.to_json()
    print(f"JSON: {json_str}")
    
    restored = RPN.from_json(json_str)
    print(f"Restored: {restored} = {restored.eval()}")
    
    # Infix conversion
    print(f"Infix: {expr.to_infix()}")


def real_world_examples():
    """Real-world usage examples."""
    print("\n=== Real-World Examples ===")
    
    # Quadratic formula: (-b ± √(b² - 4ac)) / 2a
    # We'll do the positive root: (-b + √(b² - 4ac)) / 2a
    quadratic = (RPNBuilder()
                .var("b").neg()                           # -b
                .var("b").push(2).pow()                   # b²
                .push(4).var("a").mul().var("c").mul()    # 4ac
                .sub().sqrt()                             # √(b² - 4ac)
                .add()                                    # -b + √(b² - 4ac)
                .push(2).var("a").mul()                   # 2a
                .div()                                    # division
                .build())
    
    # Solve x² - 5x + 6 = 0 (should give x = 2 or x = 3)
    root = quadratic.eval(a=1, b=-5, c=6)
    print(f"Quadratic formula: x² - 5x + 6 = 0, positive root = {root}")
    
    # Distance formula: √((x2-x1)² + (y2-y1)²)
    distance = (RPNBuilder()
               .var("x2").var("x1").sub().push(2).pow()   # (x2-x1)²
               .var("y2").var("y1").sub().push(2).pow()   # (y2-y1)²
               .add().sqrt()                               # √(sum)
               .build())
    
    dist = distance.eval(x1=0, y1=0, x2=3, y2=4)
    print(f"Distance: (0,0) to (3,4) = {dist}")
    
    # Compound interest: P(1 + r/n)^(nt)
    compound_interest = (RPNBuilder()
                        .var("r").var("n").div().push(1).add()  # (1 + r/n)
                        .var("n").var("t").mul()                # nt
                        .pow()                                  # (1 + r/n)^(nt)
                        .var("P").mul()                         # P * result
                        .build())
    
    # $1000 at 5% interest compounded monthly for 2 years
    amount = compound_interest.eval(P=1000, r=0.05, n=12, t=2)
    print(f"Compound interest: $1000 at 5% monthly for 2 years = ${amount:.2f}")


if __name__ == "__main__":
    basic_arithmetic()
    expression_composition()
    variables_and_templates()
    stack_operations()
    builder_pattern()
    validation_and_errors()
    serialization()
    real_world_examples()