from .constants import *


class Field:

    def __init__(self, name, start_bit, stop_bit):
        self.start_bit = start_bit
        self.stop_bit = stop_bit
        self.name = name
        self._level = 0
        self.x_offset = 0
        self.y_offset = 0

    def get_start_x(self):
        return (self.start_bit * DIMENSION_MULTIPLIER) + self.x_offset

    def get_end_x(self):
        return self.get_start_x() + self.get_width()

    def get_width(self):
        return (self.stop_bit - self.start_bit + 1) * DIMENSION_MULTIPLIER

    def get_level(self):
        return self._level

    def _set_level(self, level: int):
        self._level = level

    def _get_start_y(self):
        return self.y_offset

    def get_end_y(self):
        return self.y_offset + PACKET_HEIGHT

    def set_x_offset(self, x_offset):
        self.x_offset = x_offset

    def set_y_offset(self, y_offset):
        self.y_offset = y_offset

    def _draw(self, ctx, rect_color, text_color, bits_display_enabled):
        ctx.set_dash([])

        # Draw rectangle (field outline)
        ctx.set_source_rgb(*rect_color)
        ctx.rectangle(
            self.get_start_x(),
            self._get_start_y(),
            self.get_width(),
            PACKET_HEIGHT,
        )
        ctx.stroke()

        if bits_display_enabled == True:
            # Write start_bit and stop_bit above rectangle
            ctx.set_source_rgb(*text_color)
            ctx.move_to(
                self.get_start_x() + get_BITS_OFFSET(),
                self._get_start_y() - ctx.LINE_WIDTH,
            )
            ctx.show_text(str(self.start_bit))
            _, _, width, _, _, _ = ctx.text_extents(str(self.stop_bit))
            ctx.move_to(
                self.get_start_x() + self.get_width() - width - get_BITS_OFFSET(),
                self._get_start_y() - ctx.LINE_WIDTH,
            )
            ctx.show_text(str(self.stop_bit))

        # Write name inside rectangle
        _, _, width, height, _, _ = ctx.text_extents(self.name)
        ctx.move_to(
            self.get_start_x() + (self.get_width() / 2) - width / 2,
            self._get_start_y() + PACKET_HEIGHT / 2 + height / 2,
        )
        ctx.show_text(self.name)
