"""
There are values that can be used in pcbscript:
    number (for example: 5)
    string (for example: "this is pcbscript")
    coord (for example: 2,3)

Each value can be represented as an expression (basically a Python expression)
that can be evaluated (with eval-function) in the end of compilation process.
"""

class BaseValue:
    def __repr__(self):
        raise NotImplementedError()

    @classmethod
    def from_str(cls, s):
        raise NotImplementedError()

    def eval(self, scope={}):
        raise NotImplementedError()


class Number(BaseValue):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Number(value={self.value})"

    @classmethod
    def from_str(cls, s):
        return cls(s)

    def eval(self, scope={}):
        return eval(self.value, None, scope)


class String(BaseValue):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"String(value={self.value})"

    @classmethod
    def from_str(cls, s):
        return cls(s)

    def eval(self, scope={}):
        raise ValueError("eval is not allowed for strings")


class Coord(BaseValue):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Coord(x={self.x}, y={self.y})"

    @classmethod
    def from_str(cls, s):
        xy = s.split(',', 1)
        return cls(*xy)

    def eval(self, scope={}):
        x = eval(self.x, None, scope)
        y = eval(self.y, None, scope)
        return (x, y)
