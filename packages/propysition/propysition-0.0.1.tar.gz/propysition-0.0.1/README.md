# Propysition Logic Package
propysition is a Python package for propositional logic. It allows you to define propositional variables, build complex logical expressions, form arguments, and generate truth tables. This package is designed to help students and enthusiasts study and analyze propositional logic efficiently.

## Features
- Define propositional variables with optional descriptions
- Build logical expressions using AND, OR, NOT, XOR, and IMPLIES
- Form arguments with premises and conclusions
- Generate and display truth tables
- Check argument validity, tautologies, and contradictions

## Installation
- Install from PyPI:
```
pip install propysition
```

## Usage Example
```python
from propysition import Variable, And, Or, Not, Xor, Implies, Argument

a = Variable("A", "It is raining")
b = Variable("B", "I have an umbrella")
expr = And(a, Not(b))
print(expr)  # (A ∧ (¬B))

assignment = {a: True, b: False}
print(expr.evaluate(assignment))  # True

premise1 = a | b
premise2 = a & ~b
conclusion = And(a, Not(b))
argument = Argument([premise1, premise2], conclusion)
print(argument)
argument.truth_table()
```


## Documentation
See the docstrings in the code for details on each class and method.

## License
MIT License