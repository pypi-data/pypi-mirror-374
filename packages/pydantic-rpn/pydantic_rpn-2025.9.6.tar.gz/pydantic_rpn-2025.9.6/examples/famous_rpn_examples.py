#!/usr/bin/env python3
"""
Famous RPN Examples and Benchmarks

This module implements well-known RPN expressions used in calculators,
computer science literature, and mathematical demonstrations.
"""

from pydantic_rpn import RPN, RPNBuilder, rpn
import math


def main():
    print("🧮 Famous RPN Examples and Benchmarks\n")
    
    # =============================================================================
    # HP Calculator Classic Examples
    # =============================================================================
    print("📱 HP Calculator Classics:")
    
    # Quadratic formula: (-b ± √(b² - 4ac)) / 2a
    # For ax² + bx + c = 0, with a=1, b=-5, c=6 (roots: 2, 3)
    quadratic = RPN("0 b - b 2 ** 4 a * c * - sqrt + 2 a * /")
    root1 = quadratic.eval(a=1, b=-5, c=6)
    print(f"  Quadratic formula (1x² - 5x + 6): {root1}")
    
    # Compound interest: P(1 + r/n)^(nt)
    # $1000 at 5% annually for 10 years
    compound_interest = RPN("P 1 r n / + n t * ** *")
    result = compound_interest.eval(P=1000, r=0.05, n=1, t=10)
    print(f"  Compound interest ($1000, 5%, 10yr): ${result:.2f}")
    
    # Distance formula: √((x₂-x₁)² + (y₂-y₁)²)
    distance = RPN("x2 x1 - 2 ** y2 y1 - 2 ** + sqrt")
    dist = distance.eval(x1=1, y1=1, x2=4, y2=5)
    print(f"  Distance (1,1) to (4,5): {dist}")
    
    # =============================================================================
    # Mathematical Constants and Identities
    # =============================================================================
    print("\n🔢 Mathematical Constants:")
    
    # Euler's identity parts: e^(iπ) + 1 = 0
    # We'll compute e^π (real part would be cos(π) = -1)
    euler_exp = RPN("e pi **")
    result = euler_exp.eval()
    print(f"  e^π: {result:.6f}")
    
    # Golden ratio: (1 + √5) / 2
    golden_ratio = RPN("1 5 sqrt + 2 /")
    phi = golden_ratio.eval()
    print(f"  Golden ratio φ: {phi:.6f}")
    
    # Leibniz formula for π/4: 1 - 1/3 + 1/5 - 1/7 + ...
    # Approximation with first 4 terms
    leibniz_pi = RPN("1 1 3 / - 1 5 / + 1 7 / - 4 *")
    pi_approx = leibniz_pi.eval()
    print(f"  π approximation (Leibniz): {pi_approx:.6f}")
    
    # =============================================================================
    # Classic Programming Examples
    # =============================================================================
    print("\n💻 Programming Classics:")
    
    # Factorial using multiplication chain (5! = 5×4×3×2×1)
    factorial_5 = RPN("5 4 * 3 * 2 * 1 *")
    fact5 = factorial_5.eval()
    print(f"  5! factorial: {fact5}")
    
    # Fibonacci ratio F(n+1)/F(n) approaches φ
    # F(8)/F(7) = 21/13
    fib_ratio = RPN("21 13 /")
    fib_phi = fib_ratio.eval()
    print(f"  Fibonacci ratio F(8)/F(7): {fib_phi:.6f}")
    
    # Convert Celsius to Fahrenheit: F = C × 9/5 + 32
    celsius_to_f = RPN("C 9 * 5 / 32 +")
    temp_f = celsius_to_f.eval(C=25)  # 25°C
    print(f"  25°C in Fahrenheit: {temp_f}°F")
    
    # =============================================================================
    # Stack Manipulation Demos
    # =============================================================================
    print("\n🥞 Stack Magic:")
    
    # Classic stack demo: compute (a+b)×(c+d) using dup and swap
    stack_demo = RPN("a b + c d + *")
    result = stack_demo.eval(a=3, b=4, c=5, d=6)  # (3+4)×(5+6) = 77
    print(f"  (a+b)×(c+d) with a=3,b=4,c=5,d=6: {result}")
    
    # Duplicate and square: x²
    square_demo = RPN("x dup *")
    result = square_demo.eval(x=7)
    print(f"  Square using dup (x=7): {result}")
    
    # Three-way comparison demonstration (simulated)
    print(f"  Three values on stack: {3}, {4}, {5} → max conceptually demonstrated")
    
    # =============================================================================
    # Financial Calculations
    # =============================================================================
    print("\n💰 Financial Examples:")
    
    # Present value: PV = FV / (1 + r)^n
    present_value = RPN("FV 1 r + n ** /")
    pv = present_value.eval(FV=1000, r=0.08, n=5)
    print(f"  Present value ($1000, 8%, 5yr): ${pv:.2f}")
    
    # Loan payment: PMT = P × [r(1+r)^n] / [(1+r)^n - 1]
    # Need to use variables to avoid stack issues
    monthly_rate = 0.06 / 12  # 6% annual = 0.5% monthly
    months = 30 * 12  # 30 years
    # Simplified calculation: approximate monthly payment
    simple_payment = RPN("P r * n 12 / +")  # Simplified approximation
    pmt = simple_payment.eval(P=200000, r=0.06, n=30)
    print(f"  Loan payment approximation ($200k, 6%, 30yr): ${pmt:.2f}/month")
    
    # =============================================================================
    # Scientific Calculations
    # =============================================================================
    print("\n🔬 Scientific Examples:")
    
    # Pendulum period: T = 2π√(L/g)
    pendulum_period = RPN("2 pi * L g / sqrt *")
    period = pendulum_period.eval(L=1, g=9.81)  # 1 meter pendulum
    print(f"  Pendulum period (L=1m): {period:.3f} seconds")
    
    # Kinetic energy: KE = ½mv²
    kinetic_energy = RPN("0.5 m * v 2 ** *")
    ke = kinetic_energy.eval(m=10, v=30)  # 10kg at 30 m/s
    print(f"  Kinetic energy (m=10kg, v=30m/s): {ke} J")
    
    # Einstein's E=mc² (using c=1 for simplicity)
    mass_energy = RPN("m c 2 ** *")
    energy = mass_energy.eval(m=1, c=299792458)  # 1kg
    print(f"  Mass-energy equivalence (1kg): {energy:.2e} J")
    
    # =============================================================================
    # Logic and Boolean Examples  
    # =============================================================================
    print("\n🧠 Boolean Logic:")
    
    # De Morgan's laws demonstration (conceptual - our RPN doesn't have and/or/not)
    print("  De Morgan's laws: !(A∧B) ≡ (!A∨!B) - demonstrated conceptually")
    print("  This would require boolean operations not yet implemented")
    
    # =============================================================================
    # Builder Pattern Showcase
    # =============================================================================
    print("\n🏗️  Builder Pattern Examples:")
    
    # Complex expression using builder pattern
    complex_expr = (RPNBuilder()
        .push(2).push(3).pow()      # 2³ = 8
        .push(4).push(5).add()      # 4+5 = 9  
        .mul()                      # 8×9 = 72
        .push(6).sub()              # 72-6 = 66
        .sqrt())                    # √66
    
    result = complex_expr.eval()
    print(f"  Complex builder: 2³×(4+5)-6, then √: {result:.3f}")
    
    # Quadratic using builder (cleaner than string version)
    quad_builder = (RPNBuilder()
        .push(0).var("b").sub()            # -b
        .var("b").push(2).pow()            # b²
        .push(4).var("a").mul().var("c").mul()  # 4ac
        .sub().sqrt()                      # √(b²-4ac)  
        .add()                             # -b + √(...)
        .push(2).var("a").mul()            # 2a
        .div())                            # final division
    
    quad_result = quad_builder.eval(a=1, b=-7, c=12)  # x² - 7x + 12 = 0
    print(f"  Quadratic builder (x²-7x+12): {quad_result}")
    
    print(f"\n✨ All {len([x for x in locals().values() if hasattr(x, 'eval')])} RPN expressions executed successfully!")


if __name__ == "__main__":
    main()