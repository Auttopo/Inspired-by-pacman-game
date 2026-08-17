
from display.display_game import DisplayGame
from display.display_ui import DisplayUI


class Display(DisplayGame, DisplayUI):
    """
    Unified display controller for the game.
    Inherits from both DisplayGame (handles maze, Pac-Man, ghosts, etc.)
    and DisplayUI (handles menus, scores, instructions, end screens).
    By combining these classes, the main game loop only needs to instantiate
    a single Display object to access all rendering methods seamlessly,
    keeping the codebase clean and modular.
    """
    pass
