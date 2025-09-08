# dual_math

dual_math - dual_math Expression Evaluator  
*A lightweight Python package for evaluating mathematical expressions in both prefix and postfix (RPN) dual_math with automatic detection.*

---

## Features
- 🔍 Auto-Detection: Automatically identifies prefix or postfix dual_math
- ⚡ Fast Evaluation: Efficient stack-based algorithm
- ➕ Operators Supported: `+`, `-`, `*`, `/` (integer division)
- 🐍 Pure Python: No external dependencies

---

## Installation
```bash
pip install dual_math
```

## USAGE

```bash
from dual_math import smartEval

result1 = smartEval(["2", "3", "+", "4", "*"])

result2 = smartEval(["*", "+", "2", "3", "4"])

print(f"Results: {result1}, {result2}")

```