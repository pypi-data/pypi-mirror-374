class Diagram:
    """
    Diagram is the base class that is used to create and draw the packet diagram.
    """

    def add_new_packet(self, name: str) -> Packet:
        """
        Adds a new packet to the diagram.

        :param name:
            name of the new packet
        :returns: the newly created :class:`Packet` instance
        """

    def draw_to_file(self, filename: str) -> None:
        """
        Draws the diagram and saves it in the specified *filename*.

        The file name must be *.svg or *.png.

        :param filename:
            name of the file where the diagram will be saved
        """

class Packet:
    """
    Packets are the main components of a Diagram. They are each composed of one or multiple :class:`Field`.

    A packet can have a :class:`Field` parent in the level directly above itself.
    """

    def set_parent(self, parent: Field) -> None:
        """
        Set the packet field parent.

        :param parent:
            the :class:`Field` parent
        """

    def add_field(self, name: str, size: int) -> Field:
        """
        Adds a new field named *name* of size *size* to the packet.

        :param name:
            name of the field that will be written inside of it
        :param size:
            size of the field
        :returns: the newly created :class:`Field` instance
        """

    def set_outline_color_rgb(self, r: float, g: float, b: float) -> None:
        """
        Sets the color of the outline rectangle of the packet.

        The color components are floating point numbers in the range 0 to 1.

        If the values passed in are outside that range, they will be clamped.

        :param r:
            red component of color
        :param g:
            green component of color
        :param b:
            blue component of color
        """

    def set_text_color_rgb(self, r: float, g: float, b: float) -> None:
        """
        Sets the color of the text of the packet.

        The color components are floating point numbers in the range 0 to 1.

        If the values passed in are outside that range, they will be clamped.

        :param r:
            red component of color
        :param g:
            green component of color
        :param b:
            blue component of color
        """

    def set_parent_lines_color_rgb(self, r: float, g: float, b: float) -> None:
        """
        Sets the color of the lines link the packet to its parent (if any).

        The color components are floating point numbers in the range 0 to 1.

        If the values passed in are outside that range, they will be clamped.

        :param r:
            red component of color
        :param g:
            green component of color
        :param b:
            blue component of color
        """

class Field:
    """
    Fields are the smallest component of a diagram. They have a name, a size and are always part of a :class:`Packet`.

    A field can be the parent of a :class:`Packet` in the level directly below itself.
    """
