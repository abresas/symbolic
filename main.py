from dataclasses import dataclass
from typing import Any


class Expression:
    def simplify(self):
        return self

    def __mul__(self, other):
        """
        >>> print(Variable('x') * 2)
        x * 2
        """
        if not isinstance(other, Expression):
            other = Constant(other)
        return Multiply(self, other)

    def __rmul__(self, other):
        """
        >>> print(2 * Variable('x'))
        2 * x
        """
        if not isinstance(other, Expression):
            other = Constant(other)
        return Multiply(other, self)

    def __add__(self, other):
        """
        >>> print(Variable('x') + 2)
        x + 2
        """
        if not isinstance(other, Expression):
            other = Constant(other)
        return Add(self, other)

    def __radd__(self, other):
        """
        >>> print(2 + Variable('x'))
        2 + x
        """
        if not isinstance(other, Expression):
            other = Constant(other)
        return Add(other, self)

    def __sub__(self, other):
        """
        >>> print(Variable('x') - 2)
        x - 2
        """
        if not isinstance(other, Expression):
            other = Constant(other)
        return Subtract(self, other)

    def __rsub__(self, other):
        """
        >>> print(2 - Variable('x'))
        2 - x
        """
        if not isinstance(other, Expression):
            other = Constant(other)
        return Subtract(other, self)

    def __truediv__(self, other):
        """
        >>> print(Variable('x') / 2)
        x / 2
        """
        if not isinstance(other, Expression):
            other = Constant(other)
        return Divide(self, other)

    def __rtruediv__(self, other):
        """
        >>> print(2 / Variable('x'))
        2 / x
        """
        if not isinstance(other, Expression):
            other = Constant(other)
        return Divide(other, self)

    def __pow__(self, other):
        """
        >>> print(Variable('x') ** 2)
        x ** 2
        """
        if not isinstance(other, Expression):
            other = Constant(other)
        return Power(self, other)

    def __rpow__(self, other):
        """
        >>> print(2 ** Variable('x'))
        2 ** x
        """
        if not isinstance(other, Expression):
            other = Constant(other)
        return Power(other, self)

@dataclass
class Constant(Expression):
    value: Any

    def __eq__(self, other):
        """
        >>> Constant(1) == Constant(1)
        True
        >>> Constant(1) == Constant(2)
        False
        >>> Constant(1) == 1
        True
        >>> Constant(1) == 2
        False
        >>> 1 == Constant(1)
        True
        >>> 2 == Constant(1)
        False
        """
        if isinstance(other, Constant):
            return self.value == other.value
        else:
            return self.value == other

    def __repr__(self):
        """
        >>> print(Constant(2))
        2
        """
        return str(self.value)

@dataclass
class Variable(Expression):
    name: str

    def __repr__(self):
        """
        >>> print(Variable('x'))
        x
        """
        return self.name

@dataclass
class Multiply(Expression):
    left: Expression
    right: Expression

    def simplify(self):
        """
        >>> x = Variable('x')
        >>> print((1 * x).simplify())
        x
        >>> print((x * 1).simplify())
        x
        >>> print((x * 2).simplify())
        2 * x
        >>> print((3 * 2 * x).simplify())
        6 * x
        >>> print((3 * (2 * x)).simplify())
        6 * x
        >>> print((3 * (x * 2)).simplify())
        6 * x
        """
        left = self.left.simplify()
        right = self.right.simplify()
        if left == 0: # annihilating element
            return Constant(0)
        if left == 1: # neutral element
            return right
        if isinstance(right, Constant) and isinstance(left, Constant): # definition of multiplication
            return Constant(right.value * left.value)
        if isinstance(right, Constant): # associativity
            return Multiply(right, left).simplify()
        if isinstance(left, Constant) and isinstance(right, Multiply) and isinstance(right.left, Constant):
            return Multiply(left * right.left, right.right).simplify()
        return Multiply(left, right)

    def __repr__(self):
        """
        >>> x = Variable('x')
        >>> print(Multiply(Constant(2), x))
        2 * x
        """
        return f'{self.left} * {self.right}'

@dataclass
class Add(Expression):
    left: Any
    right: Any

    def __repr__(self):
        """
        >>> print(Add(Constant(2), Variable('x')))
        2 + x
        """
        return f'{self.left} + {self.right}'

    def simplify(self):
        left = self.left.simplify()
        right = self.right.simplify()
        if left == 0:
            return right
        if right == 0:
            return left
        return left + right

@dataclass
class Subtract(Expression):
    left: Any
    right: Any

    def __repr__(self):
        """
        >>> print(Subtract(Constant(2), Variable('x')))
        2 - x
        """
        return f'{self.left} - {self.right}'

@dataclass
class Divide(Expression):
    left: Any
    right: Any

    def __repr__(self):
        """
        >>> print(Divide(Constant(2), Variable('x')))
        2 / x
        """
        return f'{self.left} / {self.right}'

@dataclass
class Power(Expression):
    base: Any
    exponent: Any

    def __repr__(self):
        """
        >>> print(Power(Constant(2), Variable('x')))
        2 ** x
        """
        return f'{self.base} ** {self.exponent}'

def derive(expr: Expression, var: Variable) -> Expression:
    """
    >>> x = Variable('x')
    >>> y = Variable('y')
    >>> derive(Constant(3), x)
    0
    >>> derive(y, x)
    0
    >>> derive(x, x)
    1
    >>> derive(2 * x, x)
    2
    >>> derive(2 * x + 3, x)
    2
    >>> derive(2 * x ** 3 + 3 * x + 2, x)
    6 * x ** 2 + 3
    """

    expr = expr.simplify()
    if isinstance(expr, Constant):
        return Constant(0)
    if isinstance(expr, Variable):
        if expr.name == var.name:
            return Constant(1)
        else:
            return Constant(0)
    if isinstance(expr, Multiply):
        return ((derive(expr.left, var) * expr.right) + (expr.left * derive(expr.right, var))).simplify()
    if isinstance(expr, Add):
        return (derive(expr.left, var) + derive(expr.right, var)).simplify()
    if isinstance(expr, Subtract):
        return (derive(expr.left, var) - derive(expr.right, var)).simplify()
    if isinstance(expr, Divide):
        return (((derive(expr.left, var) * expr.right) - (expr.left * derive(expr.right, var))) / (expr.right ** 2)).simplify()
    if isinstance(expr, Power):
        if isinstance(expr.exponent, Constant) and isinstance(expr.base, Variable) and expr.base == var:
            return expr.exponent * expr.base ** Constant(expr.exponent.value - 1)
    raise Exception('Derivation not implemented for: ' + str(expr))

x = Variable('x')
print(x)
print(2 * x ** 3 + 3 * x ** 2 + 4)