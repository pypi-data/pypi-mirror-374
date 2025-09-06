import pyglet

from amonite.settings import GLOBALS, Keys
from amonite.node import PositionNode

class TextNode(PositionNode):
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        text: str = "_content_",
        align: str = "center",
        anchor_x: str = "center",
        anchor_y: str = "center",
        width: float = 0.0,
        height: float | None = None,
        color: tuple = (0x00, 0x00, 0x00, 0xFF),
        font_name: str | None = None,
        font_size: int = 12,
        multiline: bool = True,
        batch: pyglet.graphics.Batch | None = None
    ) -> None:
        super().__init__(
            x = x,
            y = y
        )

        self.text = text

        self.label = pyglet.text.Label(
            text = text,
            x = x * float(GLOBALS[Keys.SCALING]),
            y = y * float(GLOBALS[Keys.SCALING]),
            z = int(z),
            multiline = multiline,
            width = int(width) * int(GLOBALS[Keys.SCALING]),
            height = int(height) * int(GLOBALS[Keys.SCALING]) if height is not None else None,
            font_name = font_name,
            font_size = font_size * float(GLOBALS[Keys.SCALING]),
            align = align,
            anchor_x = anchor_x,
            anchor_y = anchor_y,
            color = color,
            batch = batch
        )

    def delete(self) -> None:
        self.label.delete()

    def set_position(
        self,
        position: tuple[float, float],
        z: float | None = None
    ):
        self.x = position[0]
        self.label.x = position[0] * float(GLOBALS[Keys.SCALING])

        self.y = position[1]
        self.label.y = position[1] * float(GLOBALS[Keys.SCALING])

    def set_alpha(self, alpha: int) -> None:
        self.label.opacity = alpha

    def set_color(
        self,
        color: tuple = (0x00, 0x00, 0x00, 0xFF)
    ) -> None:
        self.label.color = color

    def set_text(self, text: str) -> None:
        self.label.text = text

    def draw(self) -> None:
        self.label.draw()