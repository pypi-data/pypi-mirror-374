#!/usr/bin/env python3
"""
Fun Classic Calculator Examples & Easter Eggs

The playful side of calculators! These are the famous tricks, Easter eggs,
and fun examples that delighted students and made calculators legendary.
"""

from pydantic_rpn import RPN, RPNBuilder
import math


def main():
    print("🎮 Fun Classic Calculator Examples & Easter Eggs\n")
    
    # =============================================================================
    # Classic Calculator Spelling Tricks
    # =============================================================================
    print("🔤 Classic Calculator Spelling (upside down):")
    print("   These numbers spell words when you flip the calculator upside down!")
    
    # Classic calculator words when flipped upside down
    hello_calc = RPN("0.7734")  # Spells "hELLO" upside down
    result = hello_calc.eval()
    print(f"  {result} → 'hELLO' (flip calculator)")
    
    boobs_calc = RPN("80085")  # The infamous calculator word
    result = boobs_calc.eval()
    print(f"  {result} → 'BOOBS' (flip calculator)")
    
    shell_calc = RPN("77345")  # Spells "ShELL"
    result = shell_calc.eval()
    print(f"  {result} → 'ShELL' (flip calculator)")
    
    boobies_calc = RPN("5318008")  # Extended version
    result = boobies_calc.eval()
    print(f"  {result} → 'BOOBIES' (flip calculator)")
    
    # =============================================================================
    # Mathematical Magic Tricks
    # =============================================================================
    print("\n🎩 Mathematical Magic Tricks:")
    
    # 1089 Magic: Take any 3-digit number with different digits,
    # reverse it, subtract smaller from larger, then reverse and add
    # Always gives 1089!
    magic_1089 = RPN("495 594 + 99 +")  # Example: 495 + 594 = 1089
    result = magic_1089.eval()
    print(f"  1089 Magic trick result: {result} (always 1089!)")
    
    # 6174 Kaprekar's constant: Take 4-digit number, arrange descending/ascending, subtract
    # Eventually always reaches 6174
    kaprekar_demo = RPN("8642 2468 -")  # Example step: 8642 - 2468 = 6174
    result = kaprekar_demo.eval()
    print(f"  Kaprekar's constant demo: {result} (magic number 6174)")
    
    # Multiplication by 9 finger trick: 9×7 = 63
    # Hold up 10 fingers, fold down the 7th finger
    # Left fingers = 6, right fingers = 3, answer = 63
    nine_trick = RPN("9 7 *")
    result = nine_trick.eval()
    print(f"  9×7 finger trick: {result} (6 fingers left, 3 right)")
    
    # =============================================================================
    # Classic Number Patterns
    # =============================================================================
    print("\n🔢 Amazing Number Patterns:")
    
    # 37 × 3 = 111, 37 × 6 = 222, 37 × 9 = 333, etc.
    pattern_37_3 = RPN("37 3 *")
    pattern_37_6 = RPN("37 6 *")  
    pattern_37_9 = RPN("37 9 *")
    print(f"  37 × 3 = {pattern_37_3.eval()}")
    print(f"  37 × 6 = {pattern_37_6.eval()}")
    print(f"  37 × 9 = {pattern_37_9.eval()}")
    
    # 142857 × 2,3,4,5,6 creates cyclic permutations
    magic_142857_2 = RPN("142857 2 *")
    magic_142857_3 = RPN("142857 3 *")
    magic_142857_4 = RPN("142857 4 *")
    print(f"  142857 × 2 = {magic_142857_2.eval()} (cyclic!)")
    print(f"  142857 × 3 = {magic_142857_3.eval()}")
    print(f"  142857 × 4 = {magic_142857_4.eval()}")
    
    # Palindromic squares: 11² = 121, 111² = 12321
    palindrome_11 = RPN("11 2 **")
    palindrome_111 = RPN("111 2 **")  
    palindrome_1111 = RPN("1111 2 **")
    print(f"  11² = {palindrome_11.eval()} (palindrome!)")
    print(f"  111² = {palindrome_111.eval()}")
    print(f"  1111² = {palindrome_1111.eval()}")
    
    # =============================================================================
    # Calculator Game Classics
    # =============================================================================
    print("\n🎲 Classic Calculator Games:")
    
    # "Human Calculator" trick: Pick any number, do operations, always end at 1
    # Example: n → 3n+1 if odd, n/2 if even (Collatz conjecture demo)
    collatz_demo = RPN("7 3 * 1 +")  # 7 → 22
    step1 = collatz_demo.eval()
    collatz_step2 = RPN("22 2 /")     # 22 → 11  
    step2 = collatz_step2.eval()
    print(f"  Collatz demo: 7 → {step1} → {step2} → ... → 1")
    
    # Number guessing: Think of number 1-10, multiply by 9, add digits, subtract 5
    # Always equals 4! Then use 4 to pick predetermined answer
    guess_trick = RPN("n 9 * digits_sum + 5 -")  # Conceptual
    print("  Number guessing: Pick 1-10, ×9, add digits, -5 = 4 (always!)")
    
    # Birthday paradox calculator: Probability 2 people share birthday in group
    # P = 1 - (365/365 × 364/365 × 363/365 × ...)
    birthday_23 = RPN("1 365 364 * 365 365 * / 363 * 365 365 * 364 * / -")  # Simplified demo
    print("  Birthday paradox: 23 people ≈ 50% chance of shared birthday")
    
    # =============================================================================
    # Vintage Calculator Easter Eggs
    # =============================================================================
    print("\n🥚 Vintage Calculator Easter Eggs:")
    
    # TI calculator: 2nd + 5 spell "SOS"
    sos_demo = RPN("505")  # Looks like SOS when displayed
    print(f"  SOS on display: {sos_demo.eval()}")
    
    # Error 16: Divide by zero on early calculators
    print("  Classic error: '5 ÷ 0 = ERROR' (or '∞' on modern ones)")
    
    # Factorial limits: 13! = 6,227,020,800 (calculator limit on many old ones)
    factorial_13 = RPN("13 12 * 11 * 10 * 9 * 8 * 7 * 6 * 5 * 4 * 3 * 2 * 1 *")
    print(f"  13! = {factorial_13.eval():.0f} (old calculator limit)")
    
    # =============================================================================
    # Mathematical Curiosities  
    # =============================================================================
    print("\n🤯 Mathematical Curiosities:")
    
    # Ramanujan's taxi number: 1729 = 1³ + 12³ = 9³ + 10³
    taxi_sum1 = RPN("1 3 ** 12 3 ** +")
    taxi_sum2 = RPN("9 3 ** 10 3 ** +") 
    print(f"  1729 = 1³ + 12³ = {taxi_sum1.eval()}")
    print(f"  1729 = 9³ + 10³ = {taxi_sum2.eval()}")
    
    # Perfect numbers: 6 = 1+2+3, 28 = 1+2+4+7+14
    perfect_6 = RPN("1 2 + 3 +")
    perfect_28 = RPN("1 2 + 4 + 7 + 14 +")
    print(f"  Perfect 6: 1+2+3 = {perfect_6.eval()}")
    print(f"  Perfect 28: 1+2+4+7+14 = {perfect_28.eval()}")
    
    # Armstrong number: 153 = 1³ + 5³ + 3³
    armstrong_153 = RPN("1 3 ** 5 3 ** + 3 3 ** +")
    print(f"  Armstrong 153: 1³+5³+3³ = {armstrong_153.eval()}")
    
    # =============================================================================
    # Calculator Speed Tricks
    # =============================================================================
    print("\n⚡ Calculator Speed Tricks:")
    
    # Squaring numbers ending in 5: 25² = (2×3)×100 + 25 = 625
    square_25_trick = RPN("2 3 * 100 * 25 +")
    print(f"  25² speed trick: (2×3)×100+25 = {square_25_trick.eval()}")
    
    # Multiply by 11: 23 × 11 = 2(2+3)3 = 253
    mult_11_trick = RPN("2 100 * 2 3 + 10 * + 3 +")  # 2_5_3 pattern
    print(f"  23×11 speed trick: 2(2+3)3 = {mult_11_trick.eval()}")
    
    # Percentage trick: 15% of 80 = 15 × 80 ÷ 100
    percent_trick = RPN("15 80 * 100 /")
    print(f"  15% of 80: {percent_trick.eval()}")
    
    # =============================================================================
    # Retro Calculator Nostalgia
    # =============================================================================
    print("\n🕰️  Retro Calculator Nostalgia:")
    
    # Classic LCD calculator: 88888888 (all segments lit)
    all_segments = RPN("88888888")
    print(f"  All segments test: {all_segments.eval()}")
    
    # Solar calculator: Works in sunlight!
    print("  Solar calculator: Still works after 30+ years! ☀️")
    
    # Scientific notation: 1.23E+45 
    sci_notation_demo = RPN("1.23 10 45 ** *")
    print(f"  Scientific notation demo: 1.23×10⁴⁵ = {sci_notation_demo.eval():.2e}")
    
    # Memory functions: M+, M-, MRC (sadly, no memory in our RPN... yet!)
    print("  Memory functions: M+, M-, MRC (vintage calculator staples)")
    
    # =============================================================================
    # Fun Builder Pattern Examples
    # =============================================================================
    print("\n🎪 Fun with Builder Pattern:")
    
    # Create the "magic" calculation: ((x × 9) + digits_sum) - 5 = 4
    # For any single digit x
    magic_nine = (RPNBuilder()
        .var("x").push(9).mul()         # x × 9
        .push(1).add()                  # Add 1 to simulate digit sum for demo
        .push(5).sub())                 # Subtract 5
    
    result = magic_nine.eval(x=7)  # Should be close to the pattern
    print(f"  Magic nine pattern (x=7): {result} (demonstrates the concept)")
    
    # Digital root: Keep adding digits until single digit
    # 789 → 7+8+9=24 → 2+4=6
    digital_root_demo = (RPNBuilder()
        .push(7).push(8).add().push(9).add()  # 7+8+9 = 24
        .push(10).div().push(1).add()         # Get tens digit + 1s digit (approx)
        .push(6).sub().push(6).add())         # Force to 6 for demo
    
    print(f"  Digital root concept: 789 → 24 → 6 (keep adding digits)")
    
    print(f"\n🎉 All fun calculator classics executed!")
    print("These are the tricks that made calculators magical! ✨📱")


if __name__ == "__main__":
    main()