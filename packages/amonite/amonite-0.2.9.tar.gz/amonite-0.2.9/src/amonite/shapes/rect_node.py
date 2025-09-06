from typing import Optional, Tuple
import pyglet

from amonite.settings import GLOBALS, Keys
from amonite.shapes.shape_node import ShapeNode

class RectNode(ShapeNode):
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        width: float = 0.0,
        height: float = 0.0,
        anchor_x: float = 0,
        anchor_y: float = 0,
        color: tuple[int, int, int, int] = (0x00, 0x00, 0x00, 0x7F),
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(
            x = x,
            y = y,
            z = z,
            color = color
        )

        self.__width = width
        self.__height = height

        self.__shape: pyglet.shapes.Rectangle = pyglet.shapes.Rectangle(
            x = x * float(GLOBALS[Keys.SCALING]),
            y = y * float(GLOBALS[Keys.SCALING]),
            width = width * float(GLOBALS[Keys.SCALING]),
            height = height * float(GLOBALS[Keys.SCALING]),
            color = color,
            group = pyglet.graphics.Group(order = int(z)),
            batch = batch
        )
        self.__shape.z = z
        self.__shape.anchor_position = (anchor_x * float(GLOBALS[Keys.SCALING]), anchor_y * float(GLOBALS[Keys.SCALING]))

    def delete(self) -> None:
        self.__shape.delete()

    def set_color(self, color: tuple[int, int, int]):
        super().set_color(color)

        self.__shape.color = color

    def set_position(
        self,
        position: tuple[float, float],
        z: Optional[float] = None
    ) -> None:
        super().set_position(
            position = position,
            z = z
        )

        self.__shape.x = position[0] * float(GLOBALS[Keys.SCALING])
        self.__shape.y = position[1] * float(GLOBALS[Keys.SCALING])

    def get_bounds(self) -> tuple[float, float, float, float]:
        """
        Computes and returns the rectangle position and size in the form of a tuple defined as (x, y, width, height).
        """
        
        return (*self.get_position(), self.__width, self.__height)

    def set_bounds(self, bounds: tuple[float, float, float, float]) -> None:
        """
        Sets the rectangle position and size.

        [bounds] is a tuple defined as (x, y, width, height).
        """

        self.set_position(bounds[:2])
        self.__width = bounds[2]
        self.__height = bounds[3]
        self.__shape.width = bounds[2] * float(GLOBALS[Keys.SCALING])
        self.__shape.height = bounds[3] * float(GLOBALS[Keys.SCALING])

    def set_alpha(self, alpha: int):
        self.__shape.opacity = alpha

    def draw(self) -> None:
        self.__shape.draw()