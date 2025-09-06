from typing import Sequence
import pyglet

from amonite import controllers
from amonite.settings import SETTINGS, Keys
from amonite.collision.collision_node import CollisionNode, CollisionType
from amonite.collision.collision_shape import CollisionRect
from amonite.interaction_node import InteractionNode
from amonite.node import PositionNode
from amonite.text_node import TextNode


class DialogNode(PositionNode):
    """
    Displays dialog when colliders with the same tags interact with it.
    """

    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        lines: list[str] | None = None,
        # Character duration in seconds.
        char_duration: float = 0.05,
        tags: Sequence[str] | None = None,
        world_batch: pyglet.graphics.Batch | None = None,
        ui_batch: pyglet.graphics.Batch | None = None,
    ) -> None:
        super().__init__(x, y)

        self.lines = lines if lines is not None else []
        self.current_char = 0
        self.current_line = 0

        self.char_duration = char_duration
        self.elapsed = 0.0

        self.interaction = InteractionNode(
            on_interaction = self.interact
        )
        controllers.INTERACTION_CONTROLLER.add_interaction(self.interaction)

        # Interaction finder.
        # This collider is responsible for searching for interactables.
        self.interactor = CollisionNode(
            x = x,
            y = y,
            sensor = True,
            collision_type = CollisionType.STATIC,
            passive_tags = [] if tags is None else list(tags),
            on_triggered = lambda tags, entered: controllers.INTERACTION_CONTROLLER.toggle(self.interaction, enable = entered),
            shape = CollisionRect(
                x = x,
                y = y,
                anchor_x = 6,
                anchor_y = 6,
                width = 12,
                height = 12,
                batch = world_batch
            )
        )
        controllers.COLLISION_CONTROLLER.add_collider(self.interactor)

        self.text = TextNode(
            # Start with no text.
            text = "",
            font_name = str(SETTINGS[Keys.FONT_NAME]),
            x = int(SETTINGS[Keys.VIEW_WIDTH]) / 2,
            y = 16.0,
            width = int(SETTINGS[Keys.VIEW_WIDTH]) * 0.8,
            batch = ui_batch
        )

        self.next_icon = TextNode(
            text = "",
            font_name = str(SETTINGS[Keys.FONT_NAME]),
            x = int(SETTINGS[Keys.VIEW_WIDTH]) - 16,
            y = 16.0,
            multiline = False,
            batch = ui_batch
        )

    def update(self, dt: float) -> None:
        if self.interaction.enabled:
            self.elapsed += dt
            if self.elapsed >= self.char_duration:
                self.elapsed = 0.0
                self.current_char += 1
                if self.current_char >= len(self.lines[self.current_line]):
                    self.current_char = len(self.lines[self.current_line])
        else:
            self.current_line = 0
            self.current_char = 0

        text: str = f"{self.lines[self.current_line][0:self.current_char]}"

        # Make the next_icon visible if the current line is ended.
        if self.current_char >= len(self.lines[self.current_line]) and self.current_line < len(self.lines) - 1:
            self.next_icon.set_text(">")
        else:
            self.next_icon.set_text("")

        self.text.set_text(text)

    def delete(self) -> None:
        self.interactor.delete()
        self.text.delete()

    def interact(self) -> None:
        """
        Progresses the dialog to the next line.
        """

        if self.interaction.enabled:
            if self.current_char < len(self.lines[self.current_line]) - 1:
                # Just go to end of the line if not there yet.
                self.current_char = len(self.lines[self.current_line]) - 1
            else:
                if self.current_line < len(self.lines) - 1:
                    # Go to next line if active and not there yet.
                    self.current_line += 1
                    self.current_char = 0
                else:
                    # End the dialog if finish line is reached already.
                    self.current_line = 0
                    self.current_char = 0
                    self.interaction.toggle(False)
        else:
            # Reopen if not already.
            self.interaction.toggle(True)