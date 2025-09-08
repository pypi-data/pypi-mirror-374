# smart_notation

smart_notation - smart_notation Expression Evaluator  
*A lightweight Python package for evaluating mathematical expressions in both prefix and postfix (RPN) smart_notation with automatic detection.*

---

## Features
- 🔍 Auto-Detection: Automatically identifies prefix or postfix smart_notation
- ⚡ Fast Evaluation: Efficient stack-based algorithm
- ➕ Operators Supported: `+`, `-`, `*`, `/` (integer division)
- 🐍 Pure Python: No external dependencies

---

## Installation
```bash
pip install smart_notation
```

## USAGE

```bash
from smart_notation import smartEval

result1 = smartEval(["2", "3", "+", "4", "*"])

result2 = smartEval(["*", "+", "2", "3", "4"])

print(f"Results: {result1}, {result2}")

```