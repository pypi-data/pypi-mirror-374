#!/usr/bin/env python3
"""
HP Calculator Classic RPN Examples

This recreates famous examples from HP calculators like the HP-35, HP-41C, and HP-12C.
These are the examples that made RPN famous among engineers and scientists.
"""

from pydantic_rpn import RPN, RPNBuilder
import math


def main():
    print("📱 HP Calculator Classic RPN Examples\n")
    
    # =============================================================================
    # HP-35 "The Original Scientific Calculator" (1972)
    # =============================================================================
    print("🔬 HP-35 Scientific Calculator Examples:")
    
    # Example from HP-35 manual: Convert 5.5° to radians
    degrees_to_radians = RPN("degrees pi * 180 /")
    result = degrees_to_radians.eval(degrees=5.5)
    print(f"  5.5° to radians: {result:.6f}")
    
    # HP-35 trig example: sin(30°) = 0.5
    sin_30 = RPN("30 pi * 180 / sin")
    result = sin_30.eval()
    print(f"  sin(30°): {result:.6f}")
    
    # Log calculations: log₁₀(1000) = 3
    log_example = RPN("1000 log")
    result = log_example.eval()
    print(f"  log₁₀(1000): {result}")
    
    # =============================================================================
    # HP-12C Financial Calculator (1981) 
    # =============================================================================
    print("\n💰 HP-12C Financial Examples:")
    
    # Simple interest: I = PRT
    simple_interest = RPN("P R * T * 100 /")
    interest = simple_interest.eval(P=1000, R=5, T=2)  # $1000 at 5% for 2 years
    print(f"  Simple interest ($1000, 5%, 2yr): ${interest}")
    
    # Future value: FV = PV(1+i)ⁿ
    future_value = RPN("PV 1 i + n ** *")
    fv = future_value.eval(PV=100, i=0.05, n=10)
    print(f"  Future value ($100, 5%, 10yr): ${fv:.2f}")
    
    # Break-even point: Fixed costs ÷ (Price - Variable cost)
    break_even = RPN("FC P VC - /")
    units = break_even.eval(FC=10000, P=25, VC=15)  # $10k fixed, $25 price, $15 variable
    print(f"  Break-even (FC=$10k, P=$25, VC=$15): {units} units")
    
    # =============================================================================
    # HP-41C Advanced Examples (1979)
    # =============================================================================
    print("\n🚀 HP-41C Advanced Examples:")
    
    # Coordinate conversion: Polar to rectangular
    # x = r cos θ, y = r sin θ
    polar_to_x = RPN("r theta cos *")
    polar_to_y = RPN("r theta sin *")
    x = polar_to_x.eval(r=10, theta=math.pi/4)  # 45°
    y = polar_to_y.eval(r=10, theta=math.pi/4)
    print(f"  Polar (r=10, θ=45°) to rectangular: x={x:.3f}, y={y:.3f}")
    
    # Statistical mean: Σx/n
    mean_calc = RPN("x1 x2 + x3 + x4 + x5 + 5 /")
    mean = mean_calc.eval(x1=10, x2=20, x3=30, x4=40, x5=50)
    print(f"  Mean of [10,20,30,40,50]: {mean}")
    
    # Quadratic discriminant: b² - 4ac
    discriminant = RPN("b 2 ** 4 a * c * -")
    disc = discriminant.eval(a=1, b=-5, c=6)  # x² - 5x + 6
    print(f"  Discriminant (x²-5x+6): {disc}")
    
    # =============================================================================
    # Classic Engineering Examples
    # =============================================================================
    print("\n⚙️  Classic Engineering:")
    
    # Ohm's Law: P = V²/R (power dissipation)
    power_dissipation = RPN("V 2 ** R /")
    power = power_dissipation.eval(V=12, R=4)  # 12V across 4Ω
    print(f"  Power dissipation (12V, 4Ω): {power}W")
    
    # Resonant frequency: f = 1/(2π√LC)
    resonant_freq = RPN("1 2 pi * L C * sqrt * /")
    freq = resonant_freq.eval(L=0.001, C=0.000001)  # 1mH, 1µF
    print(f"  Resonant frequency (L=1mH, C=1µF): {freq:.0f} Hz")
    
    # Area of triangle: A = ½ab sin(C)
    triangle_area = RPN("a b * C sin * 2 /")
    area = triangle_area.eval(a=5, b=8, C=math.pi/3)  # sides 5,8 with 60° angle
    print(f"  Triangle area (a=5, b=8, C=60°): {area:.2f}")
    
    # =============================================================================
    # Stack Showcase (What made HP calculators famous)
    # =============================================================================
    print("\n🥞 Famous Stack Operations:")
    
    # Classic HP demo: (a+b) × (c+d) without parentheses
    # Shows the power of the stack
    cross_multiply = RPN("a b + c d + *")
    result = cross_multiply.eval(a=15, b=25, c=30, d=70)  # (15+25) × (30+70) = 4000
    print(f"  (a+b)×(c+d): (15+25)×(30+70) = {result}")
    
    # HP stack classic: x² + y² (Pythagorean)
    # Shows dup command elegance
    pythag_stack = RPN("x dup * y dup * +")
    result = pythag_stack.eval(x=3, y=4)
    print(f"  x²+y² using dup: 3²+4² = {result}")
    
    # Chain calculations: ((a+b) × c) - d) ÷ e
    chain_calc = RPN("a b + c * d - e /")
    result = chain_calc.eval(a=10, b=5, c=4, d=20, e=10)  # ((10+5)×4-20)÷10 = 4
    print(f"  Chain: ((10+5)×4-20)÷10 = {result}")
    
    # =============================================================================
    # Mathematical Classics
    # =============================================================================
    print("\n📐 Mathematical Classics:")
    
    # Heron's formula for triangle area: √[s(s-a)(s-b)(s-c)] where s = (a+b+c)/2
    # For triangle with sides 3, 4, 5
    semi_perimeter = RPN("a b + c + 2 /")
    s = semi_perimeter.eval(a=3, b=4, c=5)
    heron_area = RPN("s s a - * s b - * s c - * sqrt")
    area = heron_area.eval(s=s, a=3, b=4, c=5)
    print(f"  Heron's formula (3,4,5 triangle): {area}")
    
    # Newton's second law: F = ma, solve for acceleration
    acceleration = RPN("F m /")
    a = acceleration.eval(F=100, m=25)  # 100N force, 25kg mass
    print(f"  F=ma, solve for a: (F=100N, m=25kg) = {a} m/s²")
    
    # Surface area of sphere: 4πr²
    sphere_area = RPN("4 pi * r 2 ** *")
    area = sphere_area.eval(r=3)
    print(f"  Sphere surface area (r=3): {area:.2f}")
    
    # =============================================================================
    # Builder Pattern (Modern enhancement to classic RPN)
    # =============================================================================
    print("\n🏗️  Modern Builder Enhancement:")
    
    # Complex engineering calculation using builder
    # Electrical impedance: Z = √(R² + (ωL - 1/ωC)²)
    impedance = (RPNBuilder()
        .var("R").push(2).pow()                    # R²
        .var("w").var("L").mul()                   # ωL  
        .push(1).var("w").var("C").mul().div()     # 1/ωC
        .sub().push(2).pow()                       # (ωL - 1/ωC)²
        .add().sqrt())                             # √(R² + (...)²)
    
    z = impedance.eval(R=50, w=1000, L=0.001, C=0.000001)  # 50Ω, 1kHz, 1mH, 1µF
    print(f"  Impedance (R=50Ω, f=159Hz, L=1mH, C=1µF): {z:.2f}Ω")
    
    print(f"\n✨ All classic HP calculator examples executed successfully!")
    print("These are the calculations that made engineers fall in love with RPN! 💝")


if __name__ == "__main__":
    main()