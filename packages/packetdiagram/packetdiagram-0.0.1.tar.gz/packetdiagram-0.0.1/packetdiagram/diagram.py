import cairo
import re
from .packet import Packet
from .field import Field
from .constants import *


class Diagram:

    def __init__(self):
        self.name = ""
        self._packet_list = []
        self._max_diagram_height = 0
        self._max_diagram_width = 1000
        self._bits_display_enabled = False
        self._default_color = []

    # @classmethod
    # def from_file(cls, filename):
    #     new_diagram = cls()
    #     return new_diagram

    def parse_file(self, filename):
        pass

    def set_default_color_rgb(self, r: float, g: float, b: float):
        self._default_color = [r, g, b]

    def enable_bits_display(self):
        self._bits_display_enabled = True

    def disable_bits_display(self):
        self._bits_display_enabled = False

    def draw_to_file(self, filename: str):
        is_svg = True
        if re.search("^.*\\.(png|svg)$", filename) is not None:
            if filename.endswith(".png"):
                is_svg = False

        # Compute max width
        level = 0
        max_level_width = 0
        while (
            len([packet for packet in self._packet_list if packet.get_level() == level])
            != 0
        ):
            max_level_width = max(
                self._compute_level_width(
                    [
                        packet
                        for packet in self._packet_list
                        if packet.get_level() == level
                    ]
                ),
                max_level_width,
            )
            level += 1

        # Set diagram dimensions
        self._max_diagram_height = (
            (level * (PACKET_HEIGHT + PACKET_GAP_Y)) - PACKET_GAP_Y + Y_START
        )
        self._max_diagram_width = max_level_width

        # Update X offsets of packets
        level = 0
        while (
            len([packet for packet in self._packet_list if packet.get_level() == level])
            != 0
        ):
            self._update_packets_x_offset(
                [packet for packet in self._packet_list if packet.get_level() == level]
            )
            level += 1

        with cairo.SVGSurface(
            filename if is_svg == True else None,
            self._max_diagram_width,
            self._max_diagram_height,
        ) as surface:
            context = cairo.Context(surface)

            # Fill surface with white background
            context.set_source_rgb(1, 1, 1)
            context.rectangle(0, 0, self._max_diagram_width, self._max_diagram_height)
            context.fill()
            context.set_font_size(FONT_SIZE)
            context.set_line_width(LINE_WIDTH)

            for packet in self._packet_list:
                packet._draw(context, self._bits_display_enabled)

            if is_svg == False:
                surface.write_to_png(filename)

    def add_new_packet(self, name: str):
        self._packet_list.append(Packet(name))
        return self._packet_list[-1]

    def _compute_level_width(self, packets):
        level_width = 0
        for packet in packets:
            level_width += packet.get_width() + PACKET_GAP_X
        level_width -= PACKET_GAP_X
        return level_width

    def _update_packets_x_offset(self, packets):
        levelWidth = self._compute_level_width(packets)
        x_offset = self._get_x_center() - (levelWidth / 2)

        for packet in packets:
            packet.set_x_offset(x_offset)
            x_offset += packet.get_width() + PACKET_GAP_X

    def _get_x_center(self):
        return self._max_diagram_width / 2
