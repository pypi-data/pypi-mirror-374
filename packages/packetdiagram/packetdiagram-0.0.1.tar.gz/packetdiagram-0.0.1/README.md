**PacketDiagram** is a simple and intuitive Python library for creating packet diagrams. These diagrams allow you to visualize the structure of data packet fields, including nested subfields, and export them in **SVG** or **PNG** format.

---

## 📌 Features

- **Packet Diagram Creation**: Visualize the hierarchical structure of packets and their fields.
- **Customizable Colors**: Modify the colors of outlines, text, and parent lines.
- **Flexible Export**: Save your diagrams as **SVG** or **PNG**.
- **Intuitive API**: A simple and well-documented interface for quick adoption.

## 📦 Installation

Install **PacketDiagram** via pip :

```bash
pip install packetdiagram
```

## 🚀 Getting started

Here is a minimal example to create a basic diagram and to export it as a `.png` file

```python
import packetdiagram

# Create a new diagram
my_diagram = packetdiagram.Diagram()

# Add a packet to the diagram
packet = my_diagram.add_new_packet("Ethernet Frame")

# Add fields to the packet
packet.add_field("Destination MAC", 7)
packet.add_field("Source MAC", 7)
packet.add_field("Ether-Field", 5)
parent_field = packet.add_field("Packet", 10)
packet.add_field("FCS", 2)

# Add another packet to the diagram
packet = my_diagram.add_new_packet("Ethernet Frame")

# Set packet parent field
packet.set_parent(parent_field)

# Add fields to the second packet
packet.add_field("Source IP", 6)
packet.add_field("Destination IP", 6)
packet.add_field("Protocol", 6)
packet.add_field("...", 4)
packet.add_field("Segment", 6)

# Draw the diagram and saves it
my_diagram.draw_to_file("ethernet_frame.png")
```

**Result :**

![Basic diagram example](https://raw.githubusercontent.com/JoramFC/packetdiagram/main/docs/images/ethernet_frame.png "Basic diagram - Ethernet frame")

## 🤝 Contributing

Contributions are welcome! Here's how you can contribute:

1. Report a Bug: Open an issue on GitHub.
2. Suggest an Improvement: Open a pull request.
3. Improve Documentation: Any help to improve this README or add examples is appreciated.

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for more details.
