"""
There are commands that parse original code and
transform it into a graph of nodes.
"""

import re
import inspect

from .values import Number, String, Coord
from .nodes import *


class ParserError(Exception):
    pass


class BaseCommand:
    regex = None

    def __init__(self, args, indent):
        self.args = args
        self.indent = indent

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join(map(str, self.args))})" \
               f"[indent={self.indent}]"

    def exec_enter(self, nodes, indent_stack, macro_scope):
        raise NotImplementedError()

    def exec_exit(self, nodes, indent_stack, macro_scope, indent_idx):
        raise NodeError("exit statement not allowed")

    @classmethod
    def match(cls, line):
        match = cls.regex.match(line.lstrip())
        if match is None:
            raise ValueError("line does not match")
        return match

    @classmethod
    def from_line(cls, line):
        raise NotImplementedError()

    @classmethod
    def _get_indent(cls, line):
        lspaces = len(line) - len(line.lstrip())
        if lspaces % 4:
            raise ParserError("invalid indent")
        return lspaces // 4


class ExitCommand(BaseCommand):
    regex = re.compile(r'^exit$')

    @classmethod
    def from_line(cls, line):
        indent = cls._get_indent(line)
        return cls([], indent)

    def exec_enter(self, nodes, indent_stack, macro_scope):
        node = ExitNode()
        nodes.append(node)


class OptionCommand(BaseCommand):
    regex = re.compile(r'^option\s+([a-zA-Z\_][a-zA-Z0-9\_]*)\s*=\s*(.*?)$')

    @classmethod
    def from_line(cls, line):
        indent = cls._get_indent(line)
        name, value = cls.match(line).groups()
        args = [String.from_str(name), String(value)]
        return cls(args, indent)

    def exec_enter(self, nodes, indent_stack, macro_scope):
        node = OptionNode(self.args[0].value, self.args[1].value)
        nodes.append(node)


class BoardCommand(BaseCommand):
    regex = re.compile(r'^board\s+(.*?)$')

    @classmethod
    def from_line(cls, line):
        indent = cls._get_indent(line)
        coord_str = cls.match(line).group(1)
        args = [Coord.from_str(coord_str)]
        return cls(args, indent)

    def exec_enter(self, nodes, indent_stack, macro_scope):
        node = BoardNode(self.args[0])
        nodes.append(node)


class PinCommand(BaseCommand):
    regex = re.compile(r'^pin\s+(.*?)$')

    @classmethod
    def from_line(cls, line):
        indent = cls._get_indent(line)
        args_str = cls.match(line).group(1)

        coord_str, *extra = args_str.split()
        dout_str = extra[0] if len(extra) > 0 else 'None'
        din_str = extra[1] if len(extra) > 1 else 'None'

        args = [
            Coord.from_str(coord_str),
            Number.from_str(dout_str),
            Number.from_str(din_str),
        ]

        return cls(args, indent)

    def exec_enter(self, nodes, indent_stack, macro_scope):
        node = PinNode(*self.args)
        nodes.append(node)


class PinqCommand(BaseCommand):
    regex = re.compile(r'^pinq\s+(.*?)$')

    @classmethod
    def from_line(cls, line):
        indent = cls._get_indent(line)
        args_str = cls.match(line).group(1)

        coord_str, *extra = args_str.split()
        dout_str = extra[0] if len(extra) > 0 else 'None'
        din_str = extra[1] if len(extra) > 1 else 'None'

        args = [
            Coord.from_str(coord_str),
            Number.from_str(dout_str),
            Number.from_str(din_str),
        ]

        return cls(args, indent)

    def exec_enter(self, nodes, indent_stack, macro_scope):
        node = PinqNode(*self.args)
        nodes.append(node)


class WireCommand(BaseCommand):
    regex = re.compile(r'^wire\s+(.*?)$')

    @classmethod
    def from_line(cls, line):
        indent = cls._get_indent(line)
        args_lst = cls.match(line).group(1).split()

        try:
            float(args_lst[-1])
        except ValueError:
            coord_lst = args_lst
            width_lst = ['None']
        else:
            coord_lst = args_lst[:-1]
            width_lst = [args_lst[-1]]

        args = list(map(Coord.from_str, coord_lst)) + \
               list(map(Number.from_str, width_lst))

        return cls(args, indent)

    def exec_enter(self, nodes, indent_stack, macro_scope):
        node = WireNode(*self.args)
        nodes.append(node)


class TextCommand(BaseCommand):
    regex = re.compile(r'^text\s+\"(.*?)\"\s+(.*?)$')

    @classmethod
    def from_line(cls, line):
        indent = cls._get_indent(line)
        text, args_str = cls.match(line).groups()

        coord_str, *extra = args_str.split()
        height_str = extra[0] if len(extra) > 0 else 'None'

        args = [
            String.from_str(text),
            Coord.from_str(coord_str),
            Number.from_str(height_str),
        ]

        return cls(args, indent)

    def exec_enter(self, nodes, indent_stack, macro_scope):
        node = TextNode(*self.args)
        nodes.append(node)


class VarCommand(BaseCommand):
    regex = re.compile(r'^var\s+([a-zA-Z\_][a-zA-Z0-9\_]*)\s*=\s*(.*?)$')

    @classmethod
    def from_line(cls, line):
        indent = cls._get_indent(line)
        var_name, var_value = cls.match(line).groups()
        args = [String.from_str(var_name), Number(var_value)]
        return cls(args, indent)

    def exec_enter(self, nodes, indent_stack, macro_scope):
        node = AssignNode(self.args[0].value, self.args[1])
        nodes.append(node)


class IfCommand(BaseCommand):
    regex = re.compile(r'^if\s+(.*?)\s*:$')

    @classmethod
    def from_line(cls, line):
        indent = cls._get_indent(line)
        expr = cls.match(line).group(1)
        args = [Number(expr)]
        return cls(args, indent)

    def exec_enter(self, nodes, indent_stack, macro_scope):
        idx = len(nodes)
        indent_stack.append((idx, self))

        # Jump to the end
        # The index will be set on exit from the block
        expr = Number(f"not ({self.args[0].value})")
        node = JmpNode(None, expr)
        nodes.append(node)

    def exec_exit(self, nodes, indent_stack, macro_scope, indent_idx):
        # Jump for ELSE
        node = JmpNode(None, None)
        nodes.append(node)

        # Set index to jump on the enter of the block
        idx = len(nodes)
        nodes[indent_idx].jmp = idx


class ElseCommand(BaseCommand):
    regex = re.compile(r'^else\s*:$')

    @classmethod
    def from_line(cls, line):
        indent = cls._get_indent(line)
        return cls([], indent)

    def exec_enter(self, nodes, indent_stack, macro_scope):
        idx = len(nodes)
        indent_stack.append((idx, self))

    def exec_exit(self, nodes, indent_stack, macro_scope, indent_idx):
        idx = len(nodes)
        nodes[indent_idx - 1].jmp = idx


class ForCommand(BaseCommand):
    regex = re.compile(
        r'^for\s+([a-zA-Z\_][a-zA-Z0-9\_]*)\s+in\s+(.*?)\.\.(.*?)\s*:$'
    )

    @classmethod
    def from_line(cls, line):
        indent = cls._get_indent(line)
        var_name, value_from, value_to = cls.match(line).groups()
        args = [String.from_str(var_name), Number(value_from), Number(value_to)]
        return cls(args, indent)

    def exec_enter(self, nodes, indent_stack, macro_scope):
        idx = len(nodes)
        indent_stack.append((idx, self))

        # Assign the iterator variable
        node = AssignNode(self.args[0].value, self.args[1])
        nodes.append(node)

        # Jump to the end
        # Index to jump will be set on the end of the loop
        expr = Number(
            f"{self.args[0].value} >= {self.args[2].value}"
        )
        node = JmpNode(None, expr)
        nodes.append(node)

    def exec_exit(self, nodes, indent_stack, macro_scope, indent_idx):
        # Increment the index
        expr = Number(f"({self.args[0].value} + 1)")
        node = AssignNode(self.args[0].value, expr)
        nodes.append(node)

        # Jump to the start
        node = JmpNode(indent_idx + 1, None)
        nodes.append(node)

        # Setting index for the jump in the beginning
        # of the loop
        first_jmp_node = nodes[indent_idx + 1]
        first_jmp_node.jmp = len(nodes)


class TranslationCommand(BaseCommand):
    regex = re.compile(r'translate\s+(.*?)\s*:$')

    @classmethod
    def from_line(cls, line):
        indent = cls._get_indent(line)
        coord_str = cls.match(line).group(1)
        args = [Coord.from_str(coord_str)]
        return cls(args, indent)

    def exec_enter(self, nodes, indent_stack, macro_scope):
        node = TranslateEnterNode(self.args[0])
        idx = len(nodes)
        indent_stack.append((idx, self))
        nodes.append(node)

    def exec_exit(self, nodes, indent_stack, macro_scope, indent_idx):
        node = TranslateExitNode()
        nodes.append(node)


class RotationCommand(BaseCommand):
    regex = re.compile(r'rotate\s+(.*?)\s*:$')

    @classmethod
    def from_line(cls, line):
        indent = cls._get_indent(line)
        value_str = cls.match(line).group(1)
        args = [Number.from_str(value_str)]
        return cls(args, indent)

    def exec_enter(self, nodes, indent_stack, macro_scope):
        node = RotateEnterNode(self.args[0])
        idx = len(nodes)
        indent_stack.append((idx, self))
        nodes.append(node)

    def exec_exit(self, nodes, indent_stack, macro_scope, indent_idx):
        node = RotateExitNode()
        nodes.append(node)


class MarcoDefCommand(BaseCommand):
    regex = re.compile(
        r'macro\s+([a-zA-Z\_][a-zA-Z0-9\_]*)\s*\((.*?)\)\s*:$'
    )

    @classmethod
    def from_line(cls, line):
        indent = cls._get_indent(line)
        marco_name, args_str = cls.match(line).groups()
        args_str = args_str.strip()
        args = [String.from_str(marco_name)] + (list(map(
            String.from_str,
            map(str.strip, args_str.split(','))
        )) if args_str else [])
        return cls(args, indent)

    def exec_enter(self, nodes, indent_stack, macro_scope):
        if self.indent > 0:
            raise NodeError("invalid macro indent")

        idx = len(nodes)
        indent_stack.append((idx, self))

        # Jump to the end
        # Index will be set on the end of the macro
        node = JmpNode(None, None)
        nodes.append(node)

        # Save macro to the scope
        macro_name = self.args[0].value
        macro_scope[macro_name] = {
            'idx': idx + 1,
            'args': [arg.value for arg in self.args[1:]]
        }

    def exec_exit(self, nodes, indent_stack, macro_scope, indent_idx):
        # Going back to the call index
        node = MacroExitNode()
        nodes.append(node)

        nodes[indent_idx].jmp = len(nodes)


class MarcoCallCommand(BaseCommand):
    regex = re.compile(r'([a-zA-Z\_][a-zA-Z0-9\_]*)\s*\((.*?)\)$')

    @classmethod
    def from_line(cls, line):
        indent = cls._get_indent(line)
        marco_name, args_str = cls.match(line).groups()
        args = [String.from_str(marco_name)] + list(map(
            Number.from_str,
            map(str.strip, args_str.split(','))
        ))
        return cls(args, indent)

    def exec_enter(self, nodes, indent_stack, macro_scope):
        macro_name = self.args[0].value
        args = macro_scope[macro_name]['args']
        values = self.args[1:]

        # Assign arguments
        for arg, value in zip(args, values):
            node = AssignNode(arg, value)
            nodes.append(node)

        # Jump to the macro commands
        idx = len(nodes) + 1
        node = MacroEnterNode(macro_scope[macro_name]['idx'], idx)
        nodes.append(node)


command_classes = []


def guess_command(line):
    for command_cls in command_classes:
        try:
            command_cls.match(line)
        except ValueError:
            continue
        else:
            return command_cls.from_line(line)
    raise ParserError(f"unknown expression: {line}")


def _build_command_classes():
    del command_classes[:]
    for obj in globals().values():
        if inspect.isclass(obj) and issubclass(obj, BaseCommand) and \
                obj is not BaseCommand:
            command_classes.append(obj)


_build_command_classes()
