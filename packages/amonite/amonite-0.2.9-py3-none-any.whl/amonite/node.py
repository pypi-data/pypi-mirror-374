from amonite.settings import GLOBALS, Keys


class Node:
    __slots__ = (
        "components"
    )

    def __init__(self) -> None:
        self.components: list[Node] = []

    def draw(self) -> None:
        """
        Renders the object.
        """

    def add_component(self, component) -> None:
        """
        Adds a component to self.
        """

        self.components.append(component)

    def update(
            self,
            dt: float
        ) -> None:
        """
        Updates the whole object.
        All logic goes here.

        Parameters
        ----------
        dt: float
            Time (in s) since the last frame was calculated.
        """

    def fixed_update(
            self,
            dt: float
        ) -> None:
        """
        Updates the whole object.
        All physics-related logic should go here.

        Parameters
        ----------
        dt: float
            Time (in s) since the last frame was calculated.
        """

    def delete(self) -> None:
        """
        Deletes all components.
        """

        # Delete all components.
        for component in self.components:
            component.delete()

        # Clear the components list.
        self.components.clear()

class PositionNode(Node):
    __slots__ = (
        "start_x",
        "start_y",
        "start_z",
        "x",
        "y",
        "z"
    )

    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0
    ) -> None:
        super().__init__()
        self.start_x: float = x
        self.start_y: float = y
        self.start_z: float = z
        self.x: float = x
        self.y: float = y
        self.z: float = z

    def add_component(self, component) -> None:
        """
        Adds a component to self and sets its position.
        """

        super().add_component(component)

        if isinstance(component, PositionNode):
            component.set_position(
                position = (self.x + component.start_x, self.y + component.start_y),
                z = self.z + component.start_z
            )

    def set_position(
        self,
        position: tuple[float, float],
        z: float | None = None
    ):
        self.x = position[0]
        self.y = position[1]
        if z is not None:
            self.z = z

        # Update all components' positions.
        for component in self.components:
            if isinstance(component, PositionNode):
                component.set_position(
                    position = (
                        self.x + component.start_x,
                        self.y + component.start_y
                    ),
                    z = self.z + component.start_z
                )

    def get_position(self) -> tuple[float, float]:
        return (
            round(self.x, int(GLOBALS[Keys.FLOAT_ROUNDING])),
            round(self.y, int(GLOBALS[Keys.FLOAT_ROUNDING]))
        )

    def get_bounding_box(self) -> tuple[float, float, float, float]:
        return (self.x, self.y, 0.0, 0.0)

class GroupNode(PositionNode):
    """
    Represents a node container, which displaces its children keeping their relative positions.
    """

    __slots__ = {
        "children"
    }

    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        z: float = 0,
        children: list[PositionNode] | None = None
    ) -> None:
        super().__init__(x, y, z)

        self.children: list[PositionNode] = children if children is not None else []

    def set_position(
        self,
        position: tuple[float, float],
        z: float | None = None
    ):
        # Compute position delta.
        dp: tuple[float, float] = (position[0] - self.x, position[1] - self.y)
        dz: float = z - self.z if z is not None else 0.0

        # Set the given position.
        self.x += dp[0]
        self.y += dp[1]
        self.z += dz

        # Move all children accordingly.
        for child in self.children:
            current_child_position: tuple[float, float] = child.get_position()
            child.set_position(position = (current_child_position[0] + dp[0], current_child_position[1] + dp[1]), z = child.z + dz)

    def update(self, dt: float) -> None:
        super().update(dt)

        # Update all children.
        for child in self.children:
            child.update(dt = dt)

    def delete(self) -> None:
        for child in self.children:
            child.delete()

        self.children.clear()

        super().delete()