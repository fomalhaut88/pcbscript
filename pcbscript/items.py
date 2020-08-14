"""
There are basic result items that define the board.
Each item has full information about how it must be drawn.
"""

from collections import namedtuple


BoardItem = namedtuple('board', ['width', 'height', 'gap'])
PinItem = namedtuple('pin', ['x', 'y', 'dout', 'din'])
PinqItem = namedtuple('pinq', ['x', 'y', 'dout', 'din'])
WireItem = namedtuple('wire', ['x1', 'y1', 'x2', 'y2', 'width'])
TextItem = namedtuple('text', ['text', 'x', 'y', 'height'])


def serialize(item):
    args = ' '.join(map(_serialize_value, item))
    return f"{item.__class__.__name__} {args}"


def _serialize_value(value):
    if isinstance(value, str):
        return f'"{value}"'
    else:
        return str(value)
