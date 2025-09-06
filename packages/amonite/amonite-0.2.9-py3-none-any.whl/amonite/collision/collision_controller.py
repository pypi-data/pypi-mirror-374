from amonite.collision.collision_node import CollisionMethod, CollisionType, CollisionNode
from amonite.utils.utils import CollisionHit

VELOCITY_TOLERANCE: float = 1e-5

class CollisionController:
    def __init__(self) -> None:
        self.__colliders: dict[CollisionType, list[CollisionNode]] = {
            CollisionType.DYNAMIC: [],
            CollisionType.STATIC: []
        }

    def add_collider(
        self,
        collider: CollisionNode
    ) -> None:
        if collider.type in self.__colliders:
            self.__colliders[collider.type].append(collider)
        else:
            self.__colliders[collider.type] = [collider]

    def __scale_velocity(self, dt: float) -> None:
        if CollisionType.DYNAMIC in self.__colliders:
            for collider in self.__colliders[CollisionType.DYNAMIC]:
                collider_velocity: tuple[float, float] = collider.get_velocity()
                collider.set_velocity((collider_velocity[0] * dt, collider_velocity[1] * dt))

    def __handle_actor_collisions(self, actor: CollisionNode) -> None:
        """
        Computes all collisions on the provided actor.
        """

        if actor.method == CollisionMethod.PASSIVE:
            # Loop through static colliders.
            for other in self.__colliders[CollisionType.STATIC]:
                # Avoid calculating self-collision.
                if actor == other:
                    continue

                # Compute collision between actors.
                actor.collide(other)
        else:
            # Solve collision and iterate until velocity is exhausted.
            while abs(actor.velocity_x) > VELOCITY_TOLERANCE or abs(actor.velocity_y) > VELOCITY_TOLERANCE:
                # Save the resulting collisions for the given actor.
                nearest_collision: CollisionHit | None = None

                # Loop through static colliders.
                for other in self.__colliders[CollisionType.STATIC]:
                    # Avoid calculating self-collision.
                    if actor == other:
                        continue

                    # Compute collision between actors.
                    collision_hit: CollisionHit | None = actor.collide(other)

                    # Only save collision if it actually happened.
                    if not other.sensor and collision_hit is not None and collision_hit.time < 1.0:
                        if nearest_collision is None:
                            nearest_collision = collision_hit
                        else:
                            if collision_hit.time < nearest_collision.time:
                                nearest_collision = collision_hit

                actor_position: tuple[float, float] = actor.get_position()

                # Handling collider movement here allows us to check for all collisions before actually moving.
                if nearest_collision is not None:
                    # Move to the collision point.
                    actor.set_position((
                        actor_position[0] + actor.velocity_x * nearest_collision.time,
                        actor_position[1] + actor.velocity_y * nearest_collision.time
                    ))

                    # Compute sliding reaction.
                    x_result: float = (actor.velocity_x * abs(nearest_collision.normal.y)) * (1.0 - nearest_collision.time)
                    y_result: float = (actor.velocity_y * abs(nearest_collision.normal.x)) * (1.0 - nearest_collision.time)

                    # Set the resulting velocity for the next iteration.
                    actor.set_velocity((x_result, y_result))
                else:
                    actor.set_position((
                        actor_position[0] + actor.velocity_x,
                        actor_position[1] + actor.velocity_y
                    ))
                    actor.set_velocity((0.0, 0.0))

    def __handle_collisions(self) -> None:
        # Only check collision from dynamic to static, since dynamic/dynamic collisions are not needed for now.
        if CollisionType.DYNAMIC in self.__colliders and CollisionType.STATIC in self.__colliders:
            # Loop through dynamic colliders.
            for actor in self.__colliders[CollisionType.DYNAMIC]:
                # Trigger all collisions from the previous step.
                for other in actor.out_collisions:
                    if actor.on_triggered is not None:
                        actor.on_triggered(other.passive_tags, other, False)
                    if other.on_triggered is not None:
                        other.on_triggered(actor.active_tags, actor, False)
                for other in actor.in_collisions:
                    if actor.on_triggered is not None:
                        actor.on_triggered(other.passive_tags, other, True)
                    if other.on_triggered is not None:
                        other.on_triggered(actor.active_tags, actor, True)

                # Clear all collisions after they've been triggered.
                actor.in_collisions.clear()
                actor.out_collisions.clear()

                # Check for new collisions.
                self.__handle_actor_collisions(actor = actor)

    def update(self, dt: float) -> None:
        self.__scale_velocity(dt = dt)
        self.__handle_collisions()

    def clear(self) -> None:
        self.__colliders[CollisionType.STATIC].clear()
        self.__colliders[CollisionType.DYNAMIC].clear()

    def remove_collider(self, collider: CollisionNode):
        """
        Removes the given collider from the list, effectively preventing it from triggering collisions.
        """

        # Just return if the collider is not found.
        if not collider in self.__colliders[collider.type]:
            return

        self.__colliders[collider.type].remove(collider)

        # TODO Trigger out collisions on all other colliders.
        for other in self.__colliders[CollisionType.DYNAMIC]:
            if collider in other.collisions and other.on_triggered is not None:
                other.on_triggered(collider.passive_tags, collider, False)
