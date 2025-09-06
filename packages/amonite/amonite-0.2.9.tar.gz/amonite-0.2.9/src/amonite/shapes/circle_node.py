from typing import Optional, Tuple
import pyglet

from amonite.settings import GLOBALS, Keys
from amonite.shapes.shape_node import ShapeNode

class CircleNode(ShapeNode):
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        radius: int = 0,
        color: tuple = (0x00, 0x00, 0x00, 0xFF),
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(
            x = x,
            y = y,
            z = z,
            color = color
        )

        self.__radius = radius

        self.__shape = pyglet.shapes.Circle(
            x = x * GLOBALS[Keys.SCALING],
            y = y * GLOBALS[Keys.SCALING],
            radius = radius * GLOBALS[Keys.SCALING],
            color = color,
            batch = batch
        )
        self.__shape.z = z

    def delete(self) -> None:
        self.__shape.delete()

    def set_color(self, color: tuple[int, int, int]):
        super().set_color(color)

        self.__shape.color = color

    def set_position(
        self,
        position: tuple[float, float],
        z: float | None = None
    ) -> None:
        super().set_position(position, z)

        self.__shape.x = self.x * float(GLOBALS[Keys.SCALING])
        self.__shape.y = self.y * float(GLOBALS[Keys.SCALING])

    def set_alpha(self, alpha: int):
        self.__shape.opacity = alpha