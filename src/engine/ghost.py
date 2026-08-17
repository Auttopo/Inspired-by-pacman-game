from enum import Enum
from engine.player import Direction


class GhostState(Enum):
    """
    Defines the current behavior of the ghost.
    """
    CHASE = 1
    EDIBLE = 2
    DEAD = 3


class Ghost:
    """
    Manages the logic, position, and state of a single ghost.
    """
    def __init__(self, start_x: int, start_y: int, color_id: int) -> None:
        """
        Initializes the ghost in a corner with a specific color identity.
        """
        self.x: int = start_x
        self.y: int = start_y
        self.xf: float = start_x + 0.5
        self.yf: float = start_y + 0.5
        self.destx: float = -1
        self.desty: float = 0
        self.direction: str = "DOWN"
        self.rotasprit: int = 0
        # We save the starting position
        self.start_x: int = start_x
        self.start_y: int = start_y
        self.color_id: int = color_id
        # By default, ghosts chase the player
        self.state: GhostState = GhostState.CHASE
        # Countdown timer to handle how long they stay scared or dead
        self.timer: float = 0.0
        self.speed = 0.05

    def set_edible(self) -> None:
        """
        Triggered when Pac-Man eats a Super-pacgum. The ghost becomes edible.
        """
        if self.state != GhostState.DEAD:
            self.state = GhostState.EDIBLE
            self.timer = 6.0

    def die(self) -> None:
        """
        Triggered when Pac-Man eats this ghost. It returns to its base.
        """
        self.state = GhostState.DEAD
        self.x = self.start_x
        self.y = self.start_y
        self.xf = self.start_x + 0.5
        self.yf = self.start_y + 0.5
        self.destx = -1
        self.desty = 0
        self.direction = "DOWN"
        self.timer = 5.0  # Respawns in its corner after 5 seconds

    def update_timer(self, delta_time: float) -> None:
        """
        Updates the ghost's state timer.
        """
        if self.timer > 0:
            self.timer -= delta_time
            # If the countdown reaches zero, ghost goes back to chase mode
            if self.timer <= 0:
                self.state = GhostState.CHASE
                self.timer = 0.0
                self.current_direction = Direction.NONE

    def reset_for_new_level(self, new_x: int, new_y: int) -> None:
        """update ghosts state for a new level"""
        self.start_x = new_x
        self.start_y = new_y
        self.x = new_x
        self.y = new_y
        self.xf = new_x + 0.5
        self.yf = new_y + 0.5
        self.destx = -1
        self.desty = 0
        self.direction = "DOWN"
        self.state = GhostState.CHASE
        self.timer = 0.0
