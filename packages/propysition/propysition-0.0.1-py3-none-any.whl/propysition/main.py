"""
Propositional Logic Module

Defines classes for propositional variables, logical connectives, and arguments.
Supports evaluation and truth table generation.
"""

from __future__ import annotations
from typing import Optional, List, Set, Dict
import numpy as np
from numpy.typing import NDArray
import pandas as pd

class Proposition:
    """
    Abstract base class for all propositional logic expressions.
    """
    @property
    def variables(self) -> Set["Variable"]:
        """
        Place holder
        Returns the set of variables in this proposition.
        """
        return set()

    def evaluate(self, assignment: Dict["Variable", bool]) -> bool:
        """
        Evaluate the proposition under a given variable assignment.

        Args:
            assignment (Dict[Variable, bool]): Mapping from variables to truth values.

        Returns:
            bool: The truth value of the proposition.
        """
        raise NotImplementedError("Subclasses must implement evaluate()")

class Variable(Proposition):
    """
    Represents a propositional variable (atomic proposition).
    """
    def __init__(self, name: str, description: str = ""):
        """
        Initialize a Variable.

        Args:
            name (str): The variable's name.
            description (str, optional): Description of the variable.
        """
        self.name: str = name
        self.description: str = description

    @property
    def variables(self) -> Set["Variable"]:
        """
        Returns a set containing this variable.
        """
        return {self}

    def __repr__(self) -> str:
        """
        Returns an unambiguous string representation of the variable.
        """
        return f"Var({self.name!r}, {self.description!r})"
    
    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the variable.
        """
        return self.name

    def __and__(self, other: Proposition) -> "And":
        """
        Logical AND with another proposition.
        """
        return And(self, other)
    
    def __or__(self, other: Proposition) -> "Or":
        """
        Logical OR with another proposition.
        """
        return Or(self, other)
    
    def __xor__(self, other: Proposition) -> "Xor":
        """
        Logical XOR with another proposition.
        """
        return Xor(self, other)
    
    def __invert__(self) -> "Not":
        """
        Logical NOT of this variable.
        """
        return Not(self)

    def __rshift__(self, other: Proposition) -> "Implies":
        """
        Logical implication (one-way arrow) with another proposition.
        """
        return Implies(self, other)

    def evaluate(self, assignment: Dict["Variable", bool]) -> bool:
        """
        Evaluate the truth value of this variable under a given assignment.

        Args:
            assignment (Dict[Variable, bool]): Mapping from variables to truth values.

        Returns:
            bool: The truth value of this variable.
        """
        return assignment[self]

class And(Proposition):
    """
    Represents the logical AND of two propositions.
    """
    def __init__(self, left: Proposition, right: Proposition):
        """
        Initialize an AND proposition.

        Args:
            left (Proposition): The left operand.
            right (Proposition): The right operand.
        """
        self.left: Proposition = left
        self.right: Proposition = right

    @property
    def variables(self) -> Set["Variable"]:
        """
        Returns the set of variables in the AND proposition.
        """
        return self.left.variables | self.right.variables

    def __repr__(self) -> str:
        """
        Returns an unambiguous string representation of the AND proposition.
        """
        return f"({self.left.__repr__()} ∧ {self.right.__repr__()})"

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the AND proposition.
        """
        return f"({self.left} ∧ {self.right})"

    def evaluate(self, assignment: Dict["Variable", bool]) -> bool:
        """
        Evaluate the AND proposition under a given assignment.

        Args:
            assignment (Dict[Variable, bool]): Mapping from variables to truth values.

        Returns:
            bool: The truth value of the AND proposition.
        """
        return self.left.evaluate(assignment) and self.right.evaluate(assignment)

class Or(Proposition):
    """
    Represents the logical OR of two propositions.
    """
    def __init__(self, left: Proposition, right: Proposition):
        """
        Initialize an OR proposition.

        Args:
            left (Proposition): The left operand.
            right (Proposition): The right operand.
        """
        self.left: Proposition = left
        self.right: Proposition = right

    @property
    def variables(self) -> Set["Variable"]:
        """
        Returns the set of variables in the OR proposition.
        """
        return self.left.variables | self.right.variables

    def __repr__(self) -> str:
        """
        Returns an unambiguous string representation of the OR proposition.
        """
        return f"({self.left.__repr__()} ∨ {self.right.__repr__()})"

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the OR proposition.
        """
        return f"({self.left} ∨ {self.right})"

    def evaluate(self, assignment: Dict["Variable", bool]) -> bool:
        """
        Evaluate the OR proposition under a given assignment.

        Args:
            assignment (Dict[Variable, bool]): Mapping from variables to truth values.

        Returns:
            bool: The truth value of the OR proposition.
        """
        return self.left.evaluate(assignment) or self.right.evaluate(assignment)

class Xor(Proposition):
    """
    Represents the logical XOR of two propositions.
    """
    def __init__(self, left: Proposition, right: Proposition):
        """
        Initialize an XOR proposition.

        Args:
            left (Proposition): The left operand.
            right (Proposition): The right operand.
        """
        self.left: Proposition = left
        self.right: Proposition = right

    @property
    def variables(self) -> Set["Variable"]:
        """
        Returns the set of variables in the XOR proposition.
        """
        return self.left.variables | self.right.variables

    def __repr__(self) -> str:
        """
        Returns an unambiguous string representation of the XOR proposition.
        """
        return f"({self.left.__repr__()} ⊕ {self.right.__repr__()})"

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the XOR proposition.
        """
        return f"({self.left} ⊕ {self.right})"

    def evaluate(self, assignment: Dict["Variable", bool]) -> bool:
        """
        Evaluate the XOR proposition under a given assignment.

        Args:
            assignment (Dict[Variable, bool]): Mapping from variables to truth values.

        Returns:
            bool: The truth value of the XOR proposition.
        """
        return self.left.evaluate(assignment) != self.right.evaluate(assignment)

class Not(Proposition):
    """
    Represents the logical NOT of a proposition.
    """
    def __init__(self, operand: Proposition):
        """
        Initialize a NOT proposition.

        Args:
            operand (Proposition): The operand to negate.
        """
        self.operand: Proposition = operand

    @property
    def variables(self) -> Set["Variable"]:
        """
        Returns the set of variables in the NOT proposition.
        """
        return self.operand.variables

    def __repr__(self) -> str:
        """
        Returns an unambiguous string representation of the NOT proposition.
        """
        return f"(¬{self.operand.__repr__()})"

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the NOT proposition.
        """
        return f"(¬{self.operand})"

    def evaluate(self, assignment: Dict["Variable", bool]) -> bool:
        """
        Evaluate the NOT proposition under a given assignment.

        Args:
            assignment (Dict[Variable, bool]): Mapping from variables to truth values.

        Returns:
            bool: The truth value of the NOT proposition.
        """
        return not self.operand.evaluate(assignment)

class Implies(Proposition):
    """
    Represents logical implication (one-way arrow): left ⇒ right.
    """
    def __init__(self, left: Proposition, right: Proposition):
        """
        Initialize an implication proposition.

        Args:
            left (Proposition): The antecedent (if part).
            right (Proposition): The consequent (then part).
        """
        self.left: Proposition = left
        self.right: Proposition = right

    @property
    def variables(self) -> Set["Variable"]:
        """
        Returns the set of variables in the implication.
        """
        return self.left.variables | self.right.variables

    def __repr__(self) -> str:
        """
        Returns an unambiguous string representation of the implication.
        """
        return f"({self.left.__repr__()} ⇒ {self.right.__repr__()})"

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the implication.
        """
        return f"({self.left} ⇒ {self.right})"

    def evaluate(self, assignment: Dict["Variable", bool]) -> bool:
        """
        Evaluate the implication under a given assignment.

        Args:
            assignment (Dict[Variable, bool]): Mapping from variables to truth values.

        Returns:
            bool: The truth value of the implication.
        """
        return (not self.left.evaluate(assignment)) or self.right.evaluate(assignment)

class Argument:
    """
    Represents a logical argument with premises and a conclusion.
    """
    def __init__(self, premises: Optional[List[Proposition]] = None, conclusion: Optional[Proposition] = None):
        """
        Initialize an Argument.

        Args:
            premises (Optional[List[Proposition]]): List of premise propositions.
            conclusion (Optional[Proposition]): The conclusion proposition.
        """
        if premises is None:
            premises = []
        self.premises: List[Proposition] = premises
        self.conclusion: Optional[Proposition] = conclusion

    def add_premise(self, premise: Proposition) -> None:
        """
        Add a premise to the argument.

        Args:
            premise (Proposition): The premise to add.
        """
        self.premises.append(premise)

    def set_conclusion(self, conclusion: Proposition) -> None:
        """
        Set the conclusion of the argument.

        Args:
            conclusion (Proposition): The conclusion proposition.
        """
        self.conclusion = conclusion

    @property
    def premise_vars(self) -> Set["Variable"]:
        """
        Returns the set of all variables used in the premises.
        """
        vars: Set["Variable"] = set()
        for premise in self.premises:
            vars |= premise.variables
        return vars
    
    @property
    def conclusion_vars(self) -> Set["Variable"]:
        """
        Returns the set of all variables used in the conclusion.
        """
        if self.conclusion is not None:
            return set(self.conclusion.variables)
        return set()
    
    @property
    def var_space(self):
        """
        Returns a NumPy array of all possible truth assignments for the premise variables.
        Each row is a unique assignment.
        """
        n = len(self.premise_vars)
        return np.array(np.meshgrid(*[[0, 1]] * n)).T.reshape(-1,n)
    
    
    def evaluate(self):
        """
        Evaluate all premises and the conclusion for every possible assignment of variables.

        Returns:
            Dict[str, NDArray[np.bool_]]: Dictionary mapping column names to arrays of truth values.
        """
        premise_evals: Dict[Proposition, NDArray[np.bool_]] = {}

        # Evaluate premises
        for premise in self.premises:
            results = np.empty(self.var_space.shape[0], dtype='bool')
            for row in range(self.var_space.shape[0]):
                assignment = {var: bool(self.var_space[row, idx]) for idx, var in enumerate(self.premise_vars)}
                results[row] = premise.evaluate(assignment)
            premise_evals[premise] = results

        # Evaluate the conclusion
        conclusion_results = None
        if self.conclusion is not None:
            conclusion_results = np.empty(self.var_space.shape[0], dtype='bool')
            for row in range(self.var_space.shape[0]):
                assignment = {var: bool(self.var_space[row, idx]) for idx, var in enumerate(self.premise_vars)}
                conclusion_results[row] = self.conclusion.evaluate(assignment)

        # Build DataFrame columns for variables
        var_names = [str(var) for var in self.premise_vars]
        data = {name: self.var_space[:, idx].astype(bool) for idx, name in enumerate(var_names)}
        # Add premise evaluations
        for premise, results in premise_evals.items():
            data[str(premise)] = results
        # Add conclusion evaluation
        if self.conclusion is not None and conclusion_results is not None:
            data[f"Conclusion: {self.conclusion}"] = conclusion_results
        return data
    
    def truth_table(self):
        """
        Create a pandas DataFrame representing the truth table for the argument.

        Returns:
            pd.DataFrame: The truth table.
        """
        df = pd.DataFrame(self.evaluate())
        return df

    def __repr__(self) -> str:
        """
        Returns an unambiguous string representation of the argument,
        with each premise and the conclusion on a new line.
        """
        premises_str = '\n  '.join(repr(p) for p in self.premises)
        return f"Argument(\n  Premises:\n  {premises_str}\n  Conclusion:\n  {repr(self.conclusion)}\n)"

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the argument,
        with each premise and the conclusion on a new line.
        """
        premises_str = '\n  '.join(str(p) for p in self.premises)
        return f"Premises:\n  {premises_str}\nConclusion:\n  {self.conclusion}"