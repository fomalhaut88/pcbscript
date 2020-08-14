"""
There are nodes and their behaviour. Each node can:
    * add new items to the result;
    * change the scope of variables;
    * change motion_stack that is needed to translate or rotate coordinates
        inside translate and rotate blocks;
    * add to macro_stack where macroses (like functions) are stored;
    * fill and change options (that contain some default values);
    * stop the script;
    * jump to any other node to continue (jump can be conditional).
"""

from .items import *
from .motions import *
from .values import Number


class NodeError(Exception):
    pass


class BaseNode:
    def __repr__(self):
        return self.__class__.__name__

    def exec(self, items, scope, motion_stack, macro_stack, options):
        raise NotImplementedError()

    @classmethod
    def _eval_coord(cls, coord, scope, motion_stack):
        x, y = coord.eval(scope)
        for motion in reversed(motion_stack):
            x, y = motion.transform(x, y)
        return x, y

    @classmethod
    def _get_value_or_option(cls, expr, name, scope, options):
        value = expr.eval(scope)
        if value is None:
            value = options[name]
        return value


class ExitNode(BaseNode):
    def exec(self, items, scope, motion_stack, macro_stack, options):
        pass


class OptionNode(BaseNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def exec(self, items, scope, motion_stack, macro_stack, options):
        options[self.name] = float(self.value)


class BoardNode(BaseNode):
    def __init__(self, coord):
        self.coord = coord

    def exec(self, items, scope, motion_stack, macro_stack, options):
        width, heigth = self.coord.eval(scope)
        item = BoardItem(width, heigth, options['GAP'])
        items.append(item)


class PinNode(BaseNode):
    def __init__(self, coord, dout, din):
        self.coord = coord
        self.dout = dout
        self.din = din

    def exec(self, items, scope, motion_stack, macro_stack, options):
        x, y = self._eval_coord(self.coord, scope, motion_stack)
        dout = self._get_value_or_option(self.dout, 'PIN_DOUT', scope, options)
        din = self._get_value_or_option(self.din, 'PIN_DIN', scope, options)
        item = PinItem(x, y, dout, din)
        items.append(item)


class PinqNode(BaseNode):
    def __init__(self, coord, dout, din):
        self.coord = coord
        self.dout = dout
        self.din = din

    def exec(self, items, scope, motion_stack, macro_stack, options):
        x, y = self._eval_coord(self.coord, scope, motion_stack)
        dout = self._get_value_or_option(self.dout, 'PIN_DOUT', scope, options)
        din = self._get_value_or_option(self.din, 'PIN_DIN', scope, options)
        item = PinqItem(x, y, dout, din)
        items.append(item)


class WireNode(BaseNode):
    def __init__(self, *args):
        self.coords = args[:-1]
        self.width = args[-1]

    def exec(self, items, scope, motion_stack, macro_stack, options):
        width = self._get_value_or_option(self.width, 'WIRE_WIDTH',
                                          scope, options)
        for coord1, coord2 in zip(self.coords[:-1], self.coords[1:]):
            x1, y1 = self._eval_coord(coord1, scope, motion_stack)
            x2, y2 = self._eval_coord(coord2, scope, motion_stack)
            item = WireItem(x1, y1, x2, y2, width)
            items.append(item)


class TextNode(BaseNode):
    def __init__(self, text, coord, height):
        self.text = text
        self.coord = coord
        self.height = height

    def exec(self, items, scope, motion_stack, macro_stack, options):
        x, y = self._eval_coord(self.coord, scope, motion_stack)
        height = self._get_value_or_option(self.height, 'TEXT_HEIGHT',
                                           scope, options)
        item = TextItem(self.text.value, x, y, height)
        items.append(item)


class AssignNode(BaseNode):
    def __init__(self, var_name, expr):
        self.var_name = var_name
        self.expr = expr

    def exec(self, items, scope, motion_stack, macro_stack, options):
        scope[self.var_name] = self.expr.eval(scope)


class JmpNode(BaseNode):
    def __init__(self, jmp, expr):
        self.jmp = jmp
        self.expr = expr

    def exec(self, items, scope, motion_stack, macro_stack, options):
        value = self.expr.eval(scope) if self.expr is not None else True
        return self.jmp if value else None


class TranslateEnterNode(BaseNode):
    def __init__(self, coord):
        self.coord = coord

    def exec(self, items, scope, motion_stack, macro_stack, options):
        x, y = self.coord.eval(scope)
        motion = Translation(x, y)
        motion_stack.append(motion)


class TranslateExitNode(BaseNode):
    def exec(self, items, scope, motion_stack, macro_stack, options):
        motion_stack.pop()


class RotateEnterNode(BaseNode):
    def __init__(self, coord):
        self.coord = coord

    def exec(self, items, scope, motion_stack, macro_stack, options):
        phi = self.coord.eval(scope)
        motion = Rotation(phi)
        motion_stack.append(motion)


class RotateExitNode(BaseNode):
    def exec(self, items, scope, motion_stack, macro_stack, options):
        motion_stack.pop()


class MacroEnterNode(BaseNode):
    def __init__(self, jmp, idx):
        self.jmp = jmp
        self.idx = idx

    def exec(self, items, scope, motion_stack, macro_stack, options):
        macro_stack.append(self.idx)
        return self.jmp


class MacroExitNode(BaseNode):
    def exec(self, items, scope, motion_stack, macro_stack, options):
        return macro_stack.pop()
