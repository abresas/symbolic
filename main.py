import math
from dataclasses import dataclass
from typing import Any, List
from itertools import groupby

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
        >>> import math
        >>> print(Constant(math.e))
        e
        """
        if self.value == math.e:
            return "e"
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
        >>> print(((x ** -1) * (x ** 2)).simplify())
        x
        >>> print((3 * ((x ** -1) * (x ** 2))).simplify())
        3 * x
        >>> print(((3 * (x ** -1)) * (x ** 2)).simplify())
        3 * x
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
        if isinstance(left, Minus) and isinstance(right, Minus):
            return Multiply(left.value, right.value).simplify()
        if isinstance(left, Minus) and not isinstance(right, Minus):
            return Minus(Multiply(left.value, right).simplify())
        if isinstance(right, Minus) and not isinstance(left, Minus):
            return Minus(Multiply(left, right.value).simplify())
        if isinstance(right, Power) and isinstance(left, Power) and (right.base == left.base):
            return (right.base ** (right.exponent + left.exponent)).simplify()
        """
        if isinstance(right, Multiply) or isinstance(left, Multiply): 
            factors = self.get_factors() # -> a ** e1 * b ** e2 * a ** e3 * ... -> [(a, e1), (b, e2), (a, e3), ...]
            factors = multiply_group_factors(factors) # -> [(a, (e1+e3)), (b, e2), ...]
            return multiply_from_factors(factors).simplify() # -> a ** (e1+e3) * b ** e2 * ...
        """
        return Multiply(left, right)

    def get_factors(self) -> List['Power']:
        return get_multiplication_factors(self.right) + get_multiplication_factors(self.left)

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
        if isinstance(left, Constant) and isinstance(right, Constant):
            return Constant(left.value + right.value)
        return left + right

@dataclass
class Minus(Expression):
    value: Expression

    def simplify(self):
        value = self.value.simplify()
        if isinstance(self.value, Constant):
            return Constant(-1 * value)
        return Minus(value)

    def __repr__(self):
        if isinstance(self.value, Constant):
            return f'-{self.value}'
        else:
            return f'- {self.value}'


@dataclass
class Subtract(Expression):
    left: Any
    right: Any

    def simplify(self):
        left = self.left.simplify()
        right = self.right.simplify()
        if left == 0:
            return Minus(right)
        if right == 0:
            return left
        return left - right

    def __repr__(self):
        """
        >>> print(Subtract(Constant(2), Variable('x')))
        2 - x
        """
        return f'{self.left} - {self.right}'

@dataclass
class Divide(Expression):
    dividend: Any
    divisor: Any

    def simplify(self):
        dividend = self.dividend.simplify()
        divisor = self.divisor.simplify()
        if isinstance(dividend, Constant) and isinstance(divisor, Constant):
            # todo: gcd?
            if dividend.value % divisor.value == 0:
                return Constant(dividend.value / divisor.value)
            if divisor.value % dividend.value == 0:
                return Divide(Constant(1), Constant(divisor.value / dividend.value))
        if isinstance(dividend, Constant) and isinstance(divisor, Variable):
            return (dividend * (divisor ** (-1))).simplify()
        if isinstance(dividend, Minus) and isinstance(divisor, Minus):
            return Divide(dividend.value, divisor.value).simplify()
        if isinstance(dividend, Minus) and not isinstance(divisor, Minus):
            return Minus(Divide(dividend.value, divisor).simplify())
        if not isinstance(dividend, Minus) and isinstance(divisor, Minus):
            return Minus(Divide(dividend, divisor.value).simplify())
        return dividend / divisor

    def __repr__(self):
        """
        >>> print(Divide(Constant(2), Variable('x')))
        2 / x
        """
        return f'{self.dividend} / {self.divisor}'

@dataclass
class Logarithm(Expression):
    value: Expression
    base: int = math.e

    def simplify(self):
        value = self.value.simplify()
        base = self.base
        if value == base:
            return Constant(1)
        else:
            return Logarithm(value, base)

    def __repr__(self):
        """
        >>> print(Logarithm(10, math.e))
        ln(10)
        >>> print(Logarithm(2, 3))
        log(2, 3)
        """
        if self.base == math.e:
            return f'ln({self.value})'
        else:
            return f'log({self.value}, {self.base})'

@dataclass
class Power(Expression):
    base: Any
    exponent: Any

    def simplify(self):
        """
        >>> Power(Add(Constant(2), Constant(0)), Constant(2)).simplify()
        4
        """
        base = self.base.simplify()
        exponent = self.exponent.simplify()
        if isinstance(base, Constant) and isinstance(exponent, Constant):
            return Constant(base.value ** exponent.value)
        if isinstance(exponent, Constant) and exponent == 1:
            return base
        return Power(base, exponent)

    def __repr__(self):
        """
        >>> print(Power(Constant(2), Variable('x')))
        2 ** x
        """
        return f'{self.base} ** {self.exponent}'

def derive(expr: Expression, var: Variable) -> Expression:
    """
    >>> from math import e
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
    >>> derive(2 * x ** 3 - 3 * x + 2, x)
    6 * x ** 2 - 3
    >>> derive(x / 2, x)
    1 / 2.0
    >>> derive(2 / x, x)
    - 2 / x ** 2
    >>> derive(x ** 3, x)
    3 * x ** 2
    >>> derive(3 ** x, x)
    3 ** x * ln(3)
    >>> derive(e ** x, x)
    e ** x
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
        return (((derive(expr.dividend, var) * expr.divisor) - (expr.dividend * derive(expr.divisor, var))) / (expr.divisor ** 2)).simplify()
    if isinstance(expr, Logarithm):
        return ((1 / expr.value) * derive(expr.value, var)).simplify()
    if isinstance(expr, Power):
        return (derive(expr.exponent * Logarithm(expr.base), var) * expr).simplify()
        """
        if isinstance(expr.exponent, Constant) and isinstance(expr.base, Variable) and expr.base == var:
            return (expr.exponent * expr.base ** Constant(expr.exponent.value - 1)).simplify()
        if isinstance(expr.base, Constant) and isinstance(expr.exponent, Variable) and expr.exponent == var:
            return ((expr.base.value ** expr.exponent) * Logarithm(expr.base)).simplify()
        """
    raise Exception('Derivation not implemented for: ' + str(expr))

def get_multiplication_factors(expr: Expression) -> List[Power]:
    if isinstance(expr, Multiply):
        return expr.get_factors()
    elif isinstance(expr, Power):
        return [expr]
    else:
        return [Power(expr, Constant(1))]

def group_multiplication_factors(factors: List[Power]) -> List[Power]:
    """
    >>> group_multiplication_factors([Power(3, 1), Power(2, 2), Power(3, 2)])
    [2 ** 2, 3 ** 3]
    """
    factors = sorted(factors, key=lambda f: f.base)
    grouped_factors = []
    for base, fs in groupby(factors, lambda f: f.base):
        p = Power(base, 0)
        for f in fs:
            p.exponent += f.exponent
        grouped_factors.append(p)
    return grouped_factors