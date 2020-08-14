import math


class BaseMotion:
    def transform(self, x, y):
        raise NotImplementedError()


class Translation(BaseMotion):
    def __init__(self, x, y):
        self._x = x
        self._y = y

    def transform(self, x, y):
        return x + self._x, y + self._y


class Rotation(BaseMotion):
    def __init__(self, phi):
        self._cos = math.cos(phi * math.pi / 180)
        self._sin = math.sin(phi * math.pi / 180)

    def transform(self, x, y):
        return (x * self._cos + y * self._sin, -x * self._sin + y * self._cos)
