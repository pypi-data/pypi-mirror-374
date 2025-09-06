from .constants import *
from .field import Field


class Packet:

    def __init__(self, name: str):
        self.name = name
        self._parent = None
        self._fields = []
        self._rect_color = [0, 0, 0]
        self._text_color = [0, 0, 0]
        self._lines_color = [0, 0, 0]
        self._x_offset = 0
        self._last_field_bit_pos = 0

    def set_outline_color_rgb(self, r: float, g: float, b: float):
        self._rect_color = [r, g, b]

    def set_text_color_rgb(self, r: float, g: float, b: float):
        self._text_color = [r, g, b]

    def set_parent_lines_color_rgb(self, r: float, g: float, b: float):
        self._lines_color = [r, g, b]

    def set_parent(self, parent: Field):
        self._parent = parent

    def get_level(self):
        if self._parent is None:
            return 0
        else:
            return self._parent.get_level() + 1

    def get_width(self):
        return (max(map(lambda x: x.stop_bit, self._fields)) + 1) * DIMENSION_MULTIPLIER

    def _get_start_x(self):
        return self._x_offset

    def _get_end_x(self):
        return self._x_offset + self.get_width()

    def _get_start_y(self):
        return self._get_y_offset()

    def _get_end_y(self):
        return self._get_y_offset() + PACKET_HEIGHT

    def _get_y_offset(self):
        return self.get_level() * (PACKET_HEIGHT + PACKET_GAP_Y) + Y_START

    def set_x_offset(self, x_offset: int):
        self._x_offset = x_offset

    def set_field(self, name: str, start_bit: int, stop_bit: int):
        self._fields.append(Field(name, start_bit, stop_bit))
        return self._fields[-1]

    def add_field(self, name: str, size: int):
        self._fields.append(
            Field(
                name,
                self._last_field_bit_pos,
                self._last_field_bit_pos + size - 1,
            )
        )
        self._last_field_bit_pos += size
        return self._fields[-1]

    def _draw_parents_lines(self, ctx):
        if self._parent is not None:
            ctx.set_dash(DASH_PARAMETERS)
            ctx.set_source_rgb(*self._lines_color)

            # Left line
            ctx.move_to(self._get_start_x(), self._get_start_y())
            ctx.line_to(self._parent.get_start_x(), self._parent.get_end_y())
            ctx.stroke()

            # Right line
            ctx.move_to(self._get_end_x(), self._get_start_y())
            ctx.line_to(self._parent.get_end_x(), self._parent.get_end_y())
            ctx.stroke()

    def _draw(self, ctx, bits_display_enabled: bool):
        self._draw_parents_lines(ctx)
        for field in self._fields:
            field.set_x_offset(self._x_offset)
            field.set_y_offset(self._get_y_offset())
            field._draw(ctx, self._rect_color, self._text_color, bits_display_enabled)
