"""
Drawer takes items (the result of compilation) and
transform it into an SVG picture that is stored to the given path.
"""

import math
from io import BytesIO

import svgwrite
import cairosvg
from PIL import Image

from .items import *


class Drawer:
    def __init__(self, scale=100, color=(128, 196, 255), bg_color=(0, 16, 24)):
        self._scale = scale
        self._color = svgwrite.rgb(*color)
        self._bg_color = svgwrite.rgb(*bg_color)
        self._gap = None
        self._dwg = None
        self._main_items = []
        self._gap_items = []

    def draw(self, items):
        del self._gap_items[:]
        del self._main_items[:]

        self._dwg = None

        for item in items:
            if isinstance(item, BoardItem):
                self._define_dwg(item)
                self._draw_board(item)
            elif isinstance(item, PinItem):
                self._draw_pin(item)
            elif isinstance(item, PinqItem):
                self._draw_pinq(item)
            elif isinstance(item, TextItem):
                self._draw_text(item)
            elif isinstance(item, WireItem):
                self._draw_wire(item)

        list(map(self._dwg.add, self._gap_items))
        list(map(self._dwg.add, self._main_items))

    def save(self, path):
        if self._dwg is not None:
            self._dwg.saveas(path)

    def prepare_a4(self, path, dpi, offset, coef=1.0):
        # Converting to PNG
        bytestring = self._dwg.tostring().encode()
        output = cairosvg.svg2png(bytestring=bytestring)
        buffer = BytesIO(output)
        image = Image.open(buffer)

        # Resizing
        size_insert = (
            round(image.size[0] / self._scale / 10 * dpi * coef),
            round(image.size[1] / self._scale / 10 * dpi * coef),
        )
        image.thumbnail(size_insert, Image.ANTIALIAS)

        # Inserting into an A4 sheet
        size_a4 = (
            round(8.3 * dpi),
            round(11.7 * dpi),
        )
        offset_a4 = (
            round(offset[0] * dpi * coef),
            round(offset[1] * dpi * coef),
        )
        image_a4 = Image.new("RGB", size=size_a4, color=(255, 255, 255))
        image_a4.paste(image, offset_a4)

        # Saving the result
        image_a4.save(path)

    def _define_dwg(self, board):
        view_box = f"0 0 {board.width * self._scale} " \
                   f"{board.height * self._scale}"
        self._dwg = svgwrite.Drawing(profile='tiny', viewBox=view_box)
        self._gap = board.gap

    def _draw_board(self, board):
        color = self._color if self._gap else self._bg_color

        rect = self._dwg.rect(
            (0, 0),
            (
                board.width * self._scale,
                board.height * self._scale
            ),
            fill=color,
        )
        self._gap_items.append(rect)

        # Drawing frame if gap
        if self._gap:
            item = self._dwg.rect(
                (0, 0),
                (
                    self._gap * self._scale,
                    board.height * self._scale,
                ),
                fill=self._bg_color,
            )
            self._gap_items.append(item)

            item = self._dwg.rect(
                (0, 0),
                (
                    board.width * self._scale,
                    self._gap * self._scale,
                ),
                fill=self._bg_color,
            )
            self._gap_items.append(item)

            item = self._dwg.rect(
                ((board.width - self._gap) * self._scale, 0),
                (
                    self._gap * self._scale,
                    board.height * self._scale,
                ),
                fill=self._bg_color,
            )
            self._gap_items.append(item)

            item = self._dwg.rect(
                (0, (board.height - self._gap) * self._scale),
                (
                    board.width * self._scale,
                    self._gap * self._scale,
                ),
                fill=self._bg_color,
            )
            self._gap_items.append(item)

    def _draw_pin(self, pin):
        if self._gap:
            gap_outer = self._dwg.circle(
                (pin.x * self._scale, pin.y * self._scale),
                (0.5 * pin.dout + self._gap) * self._scale,
                fill=self._bg_color
            )
            self._gap_items.append(gap_outer)

        outer = self._dwg.circle(
            (pin.x * self._scale, pin.y * self._scale),
            0.5 * pin.dout * self._scale,
            fill=self._color
        )
        self._main_items.append(outer)

        inner = self._dwg.circle(
            (pin.x * self._scale, pin.y * self._scale),
            0.5 * pin.din * self._scale,
            fill=self._bg_color
        )
        self._main_items.append(inner)

    def _draw_pinq(self, pinq):
        if self._gap:
            outer = self._dwg.rect(
                (
                    (pinq.x - 0.5 * pinq.dout - self._gap) * self._scale,
                    (pinq.y - 0.5 * pinq.dout - self._gap) * self._scale,
                ),
                (
                    (pinq.dout + 2 * self._gap) * self._scale,
                    (pinq.dout + 2 * self._gap) * self._scale,
                ),
                fill=self._bg_color
            )
            self._gap_items.append(outer)

        outer = self._dwg.rect(
            (
                (pinq.x - 0.5 * pinq.dout) * self._scale,
                (pinq.y - 0.5 * pinq.dout) * self._scale,
            ),
            (
                pinq.dout * self._scale,
                pinq.dout * self._scale,
            ),
            fill=self._color
        )
        self._main_items.append(outer)

        inner = self._dwg.circle(
            (pinq.x * self._scale, pinq.y * self._scale),
            0.5 * pinq.din * self._scale,
            fill=self._bg_color
        )
        self._main_items.append(inner)

    def _draw_text(self, text):
        color = self._bg_color if self._gap else self._color
        text = self._dwg.text(
            text.text,
            insert=(text.x * self._scale, text.y * self._scale),
            font_size=text.height * self._scale,
            font_weight='bold',
            font_family='monospace',
            fill=color,
        )
        self._main_items.append(text)

    def _draw_wire(self, wire):
        if self._gap:
            items = self._draw_wire_step(wire, wire.width + 2 * self._gap,
                                         self._bg_color)
            self._gap_items.extend(items)

        items = self._draw_wire_step(wire, wire.width, self._color)
        self._main_items.extend(items)

    def _draw_wire_step(self, wire, width, color):
        items = []

        length = (
            (wire.x1 - wire.x2)**2 + (wire.y1 - wire.y2)**2
        )**0.5
        angle = math.atan2(
            wire.y2 - wire.y1,
            wire.x2 - wire.x1
        ) * 180 / math.pi

        rect = self._dwg.rect(
            (
                wire.x1 * self._scale,
                (wire.y1 - 0.5 * width) * self._scale
            ),
            (
                length * self._scale,
                width * self._scale
            ),
            fill=color,
            transform=f'rotate({angle} ' \
                      f'{wire.x1 * self._scale},{wire.y1 * self._scale})'
        )
        items.append(rect)

        circle1 = self._dwg.circle(
            (wire.x1 * self._scale, wire.y1 * self._scale),
            0.5 * width * self._scale,
            fill=color
        )
        items.append(circle1)

        circle2 = self._dwg.circle(
            (wire.x2 * self._scale, wire.y2 * self._scale),
            0.5 * width * self._scale,
            fill=color
        )
        items.append(circle2)

        return items
