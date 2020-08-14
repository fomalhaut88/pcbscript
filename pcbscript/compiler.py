"""
Compier manages all the process of compilation. There are 4 main steps:
    Step 1. Parsing the original code into a sequence of commands.
    Step 2. Transform the commands into a graph of nodes.
    Step 3. Execute the nodes.
    Step 4. Sorting the final items according to their priority to draw.
"""

from .nodes import ExitNode
from .items import *
from .commands import guess_command


class CompilerError(Exception):
    pass


class Compiler:
    def compile(self, code):
        # Step 1. Parsing: code -> commands
        commands = self._parse_code(code)

        # Step 2. Building execution nodes: commands -> nodes
        nodes = self._build_graph(commands)

        # Step 3. Compilation: nodes -> items
        items = self._exec_nodes(nodes)

        # Step 4. Sorting items
        self._sort_items(items)

        return items

    @classmethod
    def _cleaned_lines(cls, code):
        for line in code.split('\n'):
            line = line.split('#', 1)[0].rstrip()
            if line:
                yield line
        yield 'exit'

    def _parse_code(self, code):
        commands = []
        for line in self._cleaned_lines(code):
            command = guess_command(line)
            commands.append(command)
        return commands

    def _build_graph(self, commands):
        nodes = []
        indent_stack = []
        macro_scope = {}

        index = 0

        while index < len(commands):
            command = commands[index]

            # Check indent
            if command.indent > len(indent_stack):
                raise CompilerError("invalid indent")

            # Process indent back
            if command.indent < len(indent_stack):
                indent_idx, stack_command = indent_stack.pop()
                stack_command.exec_exit(nodes, indent_stack,
                                        macro_scope, indent_idx)

            # Process command
            else:
                command.exec_enter(nodes, indent_stack, macro_scope)
                index += 1

        return nodes

    def _exec_nodes(self, nodes):
        index = 0

        items = []
        scope = {}
        motion_stack = []
        macro_stack = []
        options = {
            'PIN_DIN': 0.25,
            'PIN_DOUT': 0.75,
            'WIRE_WIDTH': 0.375,
            'TEXT_HEIGHT': 0.75,
            'GAP': None,
        }

        while index < len(nodes):
            node = nodes[index]

            # Leave if ExitNode reached
            if isinstance(node, ExitNode):
                break

            # Execute the node
            jmp = node.exec(items, scope, motion_stack, macro_stack, options)

            # Change index
            index = jmp if jmp is not None else (index + 1)

        return items

    def _sort_items(self, items):
        items.sort(key=lambda item: (
            isinstance(item, BoardItem),
            isinstance(item, TextItem),
            isinstance(item, WireItem),
            isinstance(item, PinItem),
            isinstance(item, PinqItem),
        ), reverse=True)
