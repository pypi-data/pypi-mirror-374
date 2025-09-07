# 🧮 Pydantic RPN

> **The most delightful Python library for Reverse Polish Notation that makes HP calculator engineers weep with joy! 🚀**

[![PyPI version](https://badge.fury.io/py/pydantic-rpn.svg)](https://badge.fury.io/py/pydantic-rpn)
[![Python Support](https://img.shields.io/pypi/pyversions/pydantic-rpn.svg)](https://pypi.org/project/pydantic-rpn/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/rsp2k/pydantic-rpn/actions/workflows/test.yml/badge.svg)](https://github.com/rsp2k/pydantic-rpn/actions/workflows/test.yml)

**Finally!** A Reverse Polish Notation library that doesn't make you want to throw your calculator out the window! 🎯

If you've ever wondered what would happen if a **HP-41C calculator** had a baby with **Pydantic** and that baby was raised by **Python wizards** who appreciate both mathematical elegance AND having fun... this is it! 

## 🎪 Why This Library is Epic

- 🚀 **Lightning Fast**: Sub-millisecond evaluations that make your CPU purr
- 🔒 **Type Safe**: Pydantic-powered validation because we're not animals  
- 🎮 **Battle-Tested**: 31 brutal test cases covering everything from DOOM calculations to restaurant orders
- 🏗️ **Fluent Builder**: Chain operations like a boss with our sexy Builder pattern
- 🎯 **Zero Dependencies**: Just Pydantic and pure Python magic
- 📊 **Memory Efficient**: Zero leaks detected - your RAM will thank you
- 🔄 **Production Ready**: Used in real-world applications (restaurant delivery, anyone?)

## ⚡ Quick Start (The Fun Way!)

```bash
pip install pydantic-rpn
```

```python
from pydantic_rpn import RPN, RPNBuilder, rpn

# 🎯 Basic usage that just works
result = RPN("3 4 +").eval()  # 7
result = rpn("3 4 +")()       # 7 (because why type more?)

# 🏗️ Builder pattern for when you're feeling fancy  
result = (RPNBuilder()
    .push(3).push(4).add()
    .push(2).mul().eval())  # (3+4) * 2 = 14

# 🔥 Variables because we're not cavemen
expr = RPN("x 2 * y +")
result = expr.eval(x=5, y=3)  # 5*2 + 3 = 13

# 🎪 Stack operations that would make a HP engineer cry (happy tears)
result = RPN("5 dup *").eval()      # 5² = 25 (duplicate and multiply)
result = RPN("3 4 swap -").eval()   # 4-3 = 1 (swap then subtract)
```

## 🎮 Epic Examples

### 🍕 Restaurant Order Calculator
```python
# Real-world usage in a delivery app
order_total = RPN("item_price quantity * tax_rate 1 + * tip +")
total = order_total.eval(
    item_price=12.99, 
    quantity=2, 
    tax_rate=0.08, 
    tip=3.00
)  # $31.06 - exactly what you'd expect!
```

### 🚀 DOOM Ballistics (Yes, Really!)
```python
# Rocket splash damage calculation
splash_damage = RPN("max_damage 1 distance splash_radius / - 2 ** *")
damage = splash_damage.eval(
    max_damage=200, 
    distance=120, 
    splash_radius=128
)  # 0.78 damage at the edge - barely a scratch!
```

### 📐 HP Calculator Classics
```python
# Quadratic formula like a boss
quadratic = RPN("0 b - b 2 ** 4 a * c * - sqrt + 2 a * /")
root = quadratic.eval(a=1, b=-5, c=6)  # x² - 5x + 6 = 0 → root = 3.0

# Golden ratio because math is beautiful
golden = RPN("1 5 sqrt + 2 /").eval()  # φ = 1.618034...
```

## 🎪 The Fun Stuff

### Stack Operations (The HP Calculator Way!)
```python
rpn("5 dup *").eval()        # 25 (duplicate and multiply)
rpn("3 4 swap -").eval()     # 1  (swap then subtract)  
rpn("1 2 3 rot + +").eval()  # 6  (rotate stack, then add all)
rpn("10 3 over / +").eval()  # 13.33 (copy second item over)
```

### Mathematical Functions
```python
rpn("25 sqrt").eval()     # 5.0
rpn("pi sin").eval()      # ≈0 (sin of π)
rpn("e ln").eval()        # 1.0 (natural log of e)
rpn("-5 abs").eval()      # 5.0
```

### Variables and Templates
```python
# Variables with defaults
expr = RPN("x y +", defaults={"x": 10})
result = expr.eval(y=5)  # 15

# Template expressions for dynamic formulas
template = RPN.template("${price} ${tax} +")
result = template.eval(price=100, tax=10)  # 110
```

## 🏗️ Builder Pattern Mastery

When you need to build complex expressions programmatically:

```python
# Financial calculation: compound interest
compound_interest = (RPNBuilder()
    .var("principal")
    .push(1).var("rate").add()        # (1 + rate)
    .var("years").pow()               # (1 + rate)^years  
    .mul())                           # principal * (1 + rate)^years

result = compound_interest.eval(principal=1000, rate=0.05, years=10)
# $1,628.89 after 10 years at 5%
```

## 🎯 Advanced Features

### JSON Serialization
```python
expr = RPN("x 2 ** y 2 ** + sqrt", metadata={"formula": "pythagorean"})
json_str = expr.to_json()
restored = RPN.from_json(json_str)  # Perfect round-trip!
```

### Expression Composition
```python
expr1 = RPN("3 4 +")
expr2 = RPN("2 *")
combined = expr1 + expr2  # "3 4 + 2 *" → 14
```

### Interactive REPL
```python
from pydantic_rpn import REPL

repl = REPL()
repl.run()
# 
# rpn> 3 4 +
# 7
# rpn> ans 2 *  
# 14
```

### Command Line Interface  
```bash
# Evaluate expressions
rpn "3 4 +"                    # 7

# Use variables
rpn "x 2 *" --var x=5         # 10

# Interactive mode
rpn --repl

# Show infix notation
rpn "3 4 + 2 *" --infix       # ((3 + 4) * 2)
```

## 📊 Performance That Doesn't Suck

- **Sub-millisecond** evaluation for most expressions
- **Linear scaling** - handles 1000+ operations efficiently  
- **Zero memory leaks** detected in extensive testing
- **Production benchmarks** - ready for high-throughput applications

```python
# Benchmarks on a potato laptop:
# 1000 simple evaluations: ~4ms
# 1000 complex expressions: ~11ms  
# 100 expressions with 20 variables each: ~11ms
# This thing is FAST! 🚀
```

## 🧪 Battle-Tested Quality

- **31 brutal test cases** covering every edge case we could think of
- **Property-based testing** with Hypothesis for mathematical correctness
- **100% test coverage** because we're not monsters
- **Memory leak detection** to keep your servers happy
- **Integration tested** with real-world applications

## 🎪 Fun Examples Collection

This library comes with the most entertaining examples in mathematical computing:

- **🎮 DOOM RPN**: Ballistics calculations and demon slaying math
- **📱 HP Calculator Classics**: The formulas that made engineers fall in love with RPN
- **🕹️ Retro Computing**: From punch cards to pixels via RPN
- **🎪 Fun Calculator Tricks**: Upside-down words and mathematical magic

Check out the `examples/` directory for hours of mathematical entertainment!

## 🚀 Installation & Usage

### Requirements
- Python 3.8+
- Pydantic 2.0+
- A sense of mathematical adventure 🧭

### Install
```bash
pip install pydantic-rpn
```

### Quick Test
```python
from pydantic_rpn import rpn
assert rpn("2 3 +")() == 5  # Math still works! 🎉
```

## 🤝 Contributing

Found a bug? Want to add more mathematical mayhem? We welcome contributions!

1. Fork it ( https://github.com/rsp2k/pydantic-rpn/fork )
2. Create your feature branch (`git checkout -b my-awesome-feature`)
3. Add tests (we have standards!)
4. Make sure everything passes (`python -m pytest`)
5. Commit your changes (`git commit -am 'Add awesome feature'`)
6. Push to the branch (`git push origin my-awesome-feature`)
7. Create a Pull Request 🚀

## 📜 License

MIT License - because sharing is caring! See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- **HP Calculator Engineers** - for making RPN cool before cool was cool
- **The Pydantic Team** - for type safety that doesn't make us cry
- **John Backus** - for showing us that postfix notation is the way
- **Everyone who suffered through infix notation** - this one's for you! 🍻

---

**Made with ❤️ and excessive amounts of ☕ by developers who think math should be fun!**

*P.S. If this library doesn't make you at least 23% happier about doing math in Python, we'll refund your sense of wonder! (Offer not valid in reality, but the library is still awesome.)*

---

🕰️ **If you're into RPN, you might like my retro website**: [ryanmalloy.com](https://ryanmalloy.com) - where the 1980s never ended! 📟