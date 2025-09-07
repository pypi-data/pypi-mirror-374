#!/usr/bin/env python3
"""Test the new simplified API design"""

# Test the ideal API we want:
# from pydantic_rpn import rpn

# # Single clean way to do everything:
# result = rpn(3) + 4 * 2  # Auto-wrapping, clean syntax
# formula = rpn('revenue') - 800 * 0.1  # Variables work naturally
# complex_expr = (rpn('a') + rpn('b')) / (rpn('c') - rpn('d'))  # When you need explicit rpn()

print("Testing new API design...")
print("Goal: rpn(3) + 4 * 2 should work and generate '3 4 2 * +'")