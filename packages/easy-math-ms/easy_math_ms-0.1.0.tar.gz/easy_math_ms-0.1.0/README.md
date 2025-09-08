# easy_math

easy_math - easy_math Expression Evaluator  
*A lightweight Python package for evaluating mathematical expressions in both prefix and postfix (RPN) easy_math with automatic detection.*

---

## Features
- 🔍 Auto-Detection: Automatically identifies prefix or postfix easy_math
- ⚡ Fast Evaluation: Efficient stack-based algorithm
- ➕ Operators Supported: `+`, `-`, `*`, `/` (integer division)
- 🐍 Pure Python: No external dependencies

---

## Installation
```bash
pip install easy_math_ms
```

## USAGE

```bash
from easy_math import smartEval

result1 = smartEval(["2", "3", "+", "4", "*"])

result2 = smartEval(["*", "+", "2", "3", "4"])

print(f"Results: {result1}, {result2}")

```