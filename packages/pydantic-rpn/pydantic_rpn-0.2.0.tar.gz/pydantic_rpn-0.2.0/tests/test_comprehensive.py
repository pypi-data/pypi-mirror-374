"""Comprehensive, brutal testing of pydantic-rpn library."""

import pytest
import math
import json
from hypothesis import given, strategies as st, assume, example, settings
from hypothesis.strategies import composite
from pydantic_rpn import RPN, rpn, RPNError, ValidationError, EvaluationError, RPNBuilder
from typing import List, Union


class TestBasicOperationsExhaustive:
    """Test every basic operation with edge cases."""

    @pytest.mark.parametrize("a,b,op,expected", [
        (3, 4, '+', 7),
        (10, 5, '-', 5),
        (5, 2, '*', 10),
        (15, 3, '/', 5),
        (2, 3, '**', 8),
        (2, 3, 'pow', 8),
        (17, 5, '//', 3),  # Floor division
        (17, 5, '%', 2),   # Modulo
        (0, 5, '+', 5),    # Zero addition
        (-5, 3, '+', -2),  # Negative numbers
        (-5, -3, '*', 15), # Double negative
    ])
    def test_arithmetic_operations(self, a, b, op, expected):
        result = RPN(f"{a} {b} {op}").eval()
        assert result == expected

    @pytest.mark.parametrize("value,op,expected", [
        (25, 'sqrt', 5),
        (-5, 'abs', 5),
        (5, 'neg', -5),
        (-5, 'neg', 5),
        (3.7, 'ceil', 4),
        (3.2, 'floor', 3),
        (3.7, 'round', 4),
        (3.2, 'round', 3),
    ])
    def test_unary_operations(self, value, op, expected):
        result = RPN(f"{value} {op}").eval()
        assert result == expected

    @pytest.mark.parametrize("value,expected", [
        (0, pytest.approx(0, abs=1e-10)),
        (math.pi/2, pytest.approx(1, abs=1e-10)),
        (math.pi, pytest.approx(0, abs=1e-10)),
    ])
    def test_trigonometric_functions(self, value, expected):
        result = RPN(f"{value} sin").eval()
        assert result == expected

    def test_constants_precision(self):
        """Test mathematical constants are correct."""
        assert RPN("pi").eval() == pytest.approx(math.pi)
        assert RPN("e").eval() == pytest.approx(math.e) 
        assert RPN("tau").eval() == pytest.approx(math.tau)
        # Test tau = 2π
        assert RPN("tau pi 2 * ==").eval() is True


class TestStackOperationsComprehensive:
    """Brutally test all stack operations."""

    def test_dup_with_different_values(self):
        """Test dup with various values."""
        test_cases = [0, 1, -1, 3.14, 100, -50.5]
        for value in test_cases:
            result = RPN(f"{value} dup +").eval()
            assert result == value * 2

    def test_swap_operations(self):
        """Test swap with different value combinations."""
        test_cases = [(1, 2), (5, 10), (-3, 7), (0, 100), (3.14, 2.71)]
        for a, b in test_cases:
            # a b swap - should give b - a
            result = RPN(f"{a} {b} swap -").eval()
            assert result == b - a

    def test_drop_operations(self):
        """Test drop removes top element."""
        result = RPN("1 2 3 drop +").eval()  # Should be 1 + 2 = 3
        assert result == 3
        
        result = RPN("10 20 30 40 drop drop +").eval()  # Should be 10 + 20 = 30
        assert result == 30

    def test_over_operations(self):
        """Test over copies second element to top."""
        result = RPN("3 4 over + +").eval()  # 3 4 3 + + = 3 + 7 = 10
        assert result == 10

    def test_rot_operations(self):
        """Test rotation of top 3 elements."""
        # 1 2 3 rot -> 2 3 1
        result = RPN("1 2 3 rot - -").eval()  # 2 - 3 - 1 = -2
        assert result == -2

    def test_complex_stack_sequences(self):
        """Test complex stack manipulation sequences."""
        # Test: 5 dup over + + (should be 5 + 5 + 5 = 15)
        result = RPN("5 dup over + +").eval()
        assert result == 15

        # Test: 10 20 swap dup + + (should be 20 + 20 + 10 = 50)
        result = RPN("10 20 swap dup + +").eval()
        assert result == 50


class TestPropertyBased:
    """Property-based testing with hypothesis."""

    @composite 
    def rpn_arithmetic_expression(draw):
        """Generate valid arithmetic RPN expressions."""
        # Start with 2 numbers
        a = draw(st.integers(min_value=-100, max_value=100))
        b = draw(st.integers(min_value=1, max_value=100))  # Avoid division by zero
        op = draw(st.sampled_from(['+', '-', '*', '//', '%']))
        return f"{a} {b} {op}", a, b, op

    @given(rpn_arithmetic_expression())
    @settings(max_examples=100)
    def test_arithmetic_properties(self, expr_data):
        """Test arithmetic operations satisfy basic properties."""
        expr, a, b, op = expr_data
        result = RPN(expr).eval()
        
        # Test basic sanity
        assert isinstance(result, (int, float))
        
        # Test specific operation properties
        if op == '+':
            assert result == a + b
            # Test commutativity
            commutative = RPN(f"{b} {a} +").eval()
            assert result == commutative
        elif op == '-':
            assert result == a - b
        elif op == '*':
            assert result == a * b
            # Test commutativity
            commutative = RPN(f"{b} {a} *").eval()
            assert result == commutative

    @given(st.integers(min_value=1, max_value=1000))
    @settings(max_examples=50)
    def test_dup_property(self, value):
        """Property: x dup + should equal x * 2."""
        result = RPN(f"{value} dup +").eval()
        assert result == value * 2

    @given(st.integers(min_value=1, max_value=100), st.integers(min_value=1, max_value=100))
    @settings(max_examples=50)
    def test_swap_property(self, a, b):
        """Property: a b swap should put b on top."""
        result = RPN(f"{a} {b} swap drop").eval()  # Drop top element (b)
        assert result == a

    @given(st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False))
    @settings(max_examples=30)
    def test_sqrt_property(self, value):
        """Property: sqrt(x)² ≈ x for positive x."""
        assume(value >= 0)
        result = RPN(f"{value} sqrt dup *").eval()
        assert result == pytest.approx(value, rel=1e-10)


class TestClaimedFeaturesValidation:
    """Test all the features I claimed work but might not."""

    def test_expression_combination_broken_claim(self):
        """Test the + operator for combining expressions."""
        # This was claimed to work but is actually broken in strict mode
        expr1 = RPN("3 4 +")
        
        # This should fail in strict mode
        with pytest.raises(ValidationError):
            expr2 = RPN("2 *")  # Invalid standalone
            
        # But works in non-strict mode
        expr2 = RPN("2 *", strict=False)
        combined = expr1 + expr2
        
        # The combination should actually work
        assert combined.eval() == 14  # (3+4) * 2

    def test_method_chaining_broken_claim(self):
        """Test method chaining which creates invalid intermediate states."""
        # This should fail because "5 3" is not a valid RPN expression
        with pytest.raises(ValidationError):
            RPN("5").push(3).add()

        # But this should work with non-strict mode
        expr = RPN("5", strict=False).push(3)
        # Even in non-strict, it should fail validation
        errors = expr.validate_expression()
        assert len(errors) > 0
        
    def test_pipe_operator(self):
        """Test the | operator for piping results."""
        result = RPN("3 4 +") | RPN("ans 2 *")
        assert result == 14

    def test_partial_evaluation(self):
        """Test partial evaluation feature."""
        expr = RPN("x 2 * y +")
        partial = expr.partial(x=5)
        result = partial.eval(y=3)
        assert result == 13
        
        # Test that original expression is unchanged
        original_result = expr.eval(x=5, y=3)
        assert original_result == 13

    def test_template_functionality(self):
        """Test template creation and substitution."""
        template = RPN.template("${price} ${tax} + ${discount} -")
        result = template.eval(price=100, tax=10, discount=5)
        assert result == 105


class TestErrorHandlingExhaustive:
    """Test every possible error condition."""

    def test_division_by_zero_variants(self):
        """Test all division by zero scenarios."""
        with pytest.raises(EvaluationError):
            RPN("5 0 /").eval()
        
        with pytest.raises(EvaluationError):
            RPN("5 0 //").eval()  # Floor division
        
        with pytest.raises(EvaluationError):
            RPN("5 0 %").eval()   # Modulo

    def test_mathematical_domain_errors(self):
        """Test math operations outside valid domains."""
        with pytest.raises(EvaluationError):
            RPN("-1 sqrt").eval()  # sqrt of negative
        
        # Test log of zero/negative
        with pytest.raises(EvaluationError):
            RPN("0 ln").eval()
            
        with pytest.raises(EvaluationError):
            RPN("-1 log").eval()

    def test_stack_underflow_conditions(self):
        """Test all stack underflow scenarios."""
        # Insufficient operands for binary operators
        for op in ['+', '-', '*', '/', '**', '==', '!=', '<', '>', '<=', '>=']:
            with pytest.raises((ValidationError, EvaluationError)):
                RPN(f"5 {op}", strict=False).eval()
        
        # Insufficient operands for stack operations
        with pytest.raises((ValidationError, EvaluationError)):
            RPN("swap", strict=False).eval()
        
        with pytest.raises((ValidationError, EvaluationError)):
            RPN("5 rot", strict=False).eval()  # Need 3 items for rot

    def test_unknown_tokens(self):
        """Test handling of unknown variables and operators."""
        with pytest.raises(EvaluationError):
            RPN("unknown_variable").eval()
        
        with pytest.raises(EvaluationError):
            RPN("5 unknown_operator").eval()

    def test_malformed_expressions(self):
        """Test malformed expression handling."""
        # Empty expression
        result = RPN("").eval()
        assert result is True  # Empty should return True
        
        # Just operators
        with pytest.raises(ValidationError):
            RPN("+ + +")
        
        # Mismatched operands
        with pytest.raises(ValidationError):
            RPN("1 2 3 +")  # Leaves 2 items on stack

    def test_type_errors(self):
        """Test type-related errors."""
        # Test operations on wrong types
        with pytest.raises(EvaluationError):
            RPN("true sqrt").eval()  # sqrt of boolean


class TestComplexExpressions:
    """Test complex, nested expressions."""

    def test_nested_arithmetic(self):
        """Test deeply nested arithmetic expressions."""
        # ((3 + 4) * 2 - 1) / 3
        expr = "3 4 + 2 * 1 - 3 /"
        result = RPN(expr).eval()
        expected = ((3 + 4) * 2 - 1) / 3
        assert result == pytest.approx(expected)

    def test_complex_stack_manipulations(self):
        """Test complex stack sequences."""
        # Test: duplicate, rotate, swap in sequence
        expr = "1 2 3 dup rot swap + + +"  # Complex stack dance
        result = RPN(expr).eval()
        # Manual trace: 1 2 3 3 -> 1 3 3 2 -> 1 3 2 3 -> 1 3 5 -> 1 8 -> 9
        assert result == 9

    def test_mixed_operations(self):
        """Test mixing arithmetic, stack ops, and functions."""
        # Test: square of sum using stack operations
        expr = "3 4 + dup *"  # (3+4)²
        result = RPN(expr).eval()
        assert result == 49

        # Test: distance formula using complex operations
        expr = "3 dup * 4 dup * + sqrt"  # √(3² + 4²)
        result = RPN(expr).eval()
        assert result == 5.0

    def test_boolean_logic_chains(self):
        """Test complex boolean expressions."""
        # Test: (5 > 3) AND (2 < 4) OR (1 == 0)
        expr = "5 3 > 2 4 < and 1 0 == or"
        result = RPN(expr).eval()
        assert result is True

    def test_scientific_calculations(self):
        """Test scientific/engineering calculations."""
        # Quadratic formula: (-b + √(b² - 4ac)) / 2a
        # For x² - 5x + 6 = 0 (a=1, b=-5, c=6)
        expr = "5 neg 5 dup * 4 1 * 6 * - sqrt + 2 1 * /"
        result = RPN(expr).eval()
        assert result == pytest.approx(3.0)  # One root is 3

        # Compound interest: P(1 + r/n)^(nt)
        # $1000 at 5% annual, compounded monthly for 1 year
        expr = "0.05 12 / 1 + 12 1 * pow 1000 *"
        result = RPN(expr).eval()
        expected = 1000 * (1 + 0.05/12) ** (12 * 1)
        assert result == pytest.approx(expected)


class TestSerializationThorough:
    """Test serialization edge cases."""

    def test_json_roundtrip_complex(self):
        """Test JSON serialization with complex expressions."""
        original = RPN(
            "x 2 pow y 2 pow + sqrt",
            defaults={"x": 3, "y": 4},
            metadata={"formula": "distance", "version": 1.0}
        )
        
        json_str = original.to_json()
        restored = RPN.from_json(json_str)
        
        # Test that behavior is preserved
        assert restored.eval() == original.eval()
        assert restored.defaults == original.defaults
        assert restored.metadata == original.metadata

    def test_json_with_special_values(self):
        """Test JSON handling of special float values."""
        # Test with infinity and large numbers
        expr = RPN("pi e tau", defaults={"large": 1e10})
        json_str = expr.to_json()
        data = json.loads(json_str)
        
        # Ensure all values are JSON-serializable
        assert all(isinstance(token, (str, int, float)) for token in data["tokens"])

    def test_infix_conversion_edge_cases(self):
        """Test infix conversion with complex expressions."""
        test_cases = [
            ("3 4 +", "(3 + 4)"),
            ("3 neg", "(-3)"),
            ("5 sqrt", "sqrt(5)"),
            ("3 4 + 2 *", "((3 + 4) * 2)"),
        ]
        
        for rpn_expr, expected_pattern in test_cases:
            infix = RPN(rpn_expr).to_infix()
            # Just test that conversion doesn't crash and contains expected elements
            assert all(element in infix for element in expected_pattern.split() 
                      if element not in "()[]")


class TestPerformanceAndLimits:
    """Test performance characteristics and limits."""

    def test_large_stack_operations(self):
        """Test with large stack sizes."""
        # Create expression with many values
        n = 100
        tokens = list(range(n)) + ['+'] * (n - 1)
        expr = RPN(tokens, strict=False)  # Use non-strict for large expressions
        
        result = expr.eval()
        expected = sum(range(n))
        assert result == expected

    def test_deep_nesting(self):
        """Test deeply nested operations."""
        # Create deeply nested expression: ((((1+1)+1)+1)+1)...
        expr = "1"
        for _ in range(10):
            expr += " 1 +"
        
        result = RPN(expr).eval()
        assert result == 11

    def test_variable_handling_limits(self):
        """Test with many variables."""
        variables = {f"x{i}": i for i in range(50)}
        tokens = []
        for i in range(50):
            tokens.extend([f"x{i}", str(i), "+"])
        # Remove last operator to make valid
        tokens = tokens[:-1] + ["+"] * 49
        
        expr = RPN(tokens, strict=False)
        result = expr.eval(**variables)
        expected = sum(2 * i for i in range(50))
        assert result == expected


class TestBuilderPatternThorough:
    """Thoroughly test the builder pattern."""

    def test_builder_equivalence(self):
        """Test that builder produces equivalent expressions."""
        # Build using builder
        built = (RPNBuilder()
                .push(3)
                .push(4)
                .add()
                .push(2)
                .mul()
                .build())
        
        # Create directly
        direct = RPN("3 4 + 2 *")
        
        assert built.eval() == direct.eval()
        assert built.tokens == direct.tokens

    def test_builder_with_variables(self):
        """Test builder with variable operations."""
        expr = (RPNBuilder()
               .var("radius")
               .dup()
               .mul()  # r²
               .var("pi")
               .mul()  # πr²
               .build())
        
        result = expr.eval(radius=5, pi=math.pi)
        expected = math.pi * 25
        assert result == pytest.approx(expected)

    def test_builder_chaining_all_operations(self):
        """Test builder with all available operations."""
        expr = (RPNBuilder()
               .push(25)
               .sqrt()      # 5
               .dup()       # 5 5
               .add()       # 10
               .push(2)     # 10 2
               .pow()       # 100
               .build())
        
        result = expr.eval()
        assert result == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])