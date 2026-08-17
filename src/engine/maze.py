from typing import List
import sys
try:
    import mazegenerator
    MAZE_GENERATOR_AVAILABLE = True
except ImportError:
    MAZE_GENERATOR_AVAILABLE = False
import random

sys.setrecursionlimit(6000)


class Maze:
    """
    Manages the maze structure, walls, pacgums, and super-pacgums.
    """

    def __init__(self, width: int, height: int, seed: int) -> None:
        """
        Initializes the maze properties and generates the grid.
        """

        self.width: int = width
        self.height: int = height
        self.seed: int = seed
        # (0 = path, 1 = wall, 2 = pacgum, 3 = super-pacgum)
        self.grid: List[List[int]] = []
        self.items: List[List[int]] = [[0 for _ in range(width)]
                                       for _ in range(height)]
        self.reachable: set[tuple[int, int]] = set()
        self.generate_maze()

    def generate_maze(self) -> None:
        try:
            if not MAZE_GENERATOR_AVAILABLE:
                raise ImportError("Mazegenerator package is not installed.")
            random.seed(self.seed)
            generator = mazegenerator.MazeGenerator(
                size=(self.width, self.height),
                perfect=False,
                seed=self.seed
            )
            generator.generate(seed=self.seed)
            raw_maze = getattr(generator, 'maze',
                               getattr(generator, 'grid', []))

            self.grid = [[raw_maze[y][x] for x in range(self.width)]
                         for y in range(self.height)]
            print("Maze generated successfully using exact dimensions.")
        except Exception as e:
            print(f"[WARNING] External maze generator failed ({e}).",
                  file=sys.stderr)
            self._create_dummy_grid()
        self._place_items()

    def _create_dummy_grid(self) -> None:
        """Create a simple maze if the generator crashes."""
        self.grid = [[15 for _ in range(self.width)]
                     for _ in range(self.height)]

        for y in range(self.height):
            for x in range(self.width):
                if x % 2 == 0 or y % 2 == 0:
                    self.grid[y][x] = 0

    def _place_items(self) -> None:
        """Traverse the ENTIRE grid and place a Pac-Dot on every path."""
        # clear
        self.items = [[0 for _ in range(self.width)]
                      for _ in range(self.height)]

        # On place Super-Pacgums
        corners = [(0, 0), (self.width - 1, 0), (0, self.height - 1),
                   (self.width - 1, self.height - 1)]
        for cx, cy in corners:
            self.items[cy][cx] = 3

        #  place Pac-Gum (2)
        for y in range(self.height):
            for x in range(self.width):
                # Si c'est un chemin (0) et pas déjà une Super-Pacgum (3)
                if self.grid[y][x] != 15 and self.items[y][x] == 0:
                    self.items[y][x] = 2

        # clear the center (spawn)
        cx, cy = self.width // 2, self.height // 2
        self.items[cy][cx] = 0

    def can_move(self, x: int, y: int, direction: str) -> bool:
        """
        Checks if it is possible to leave cell (x, y) in a given direction.
        direction must be 'UP', 'RIGHT', 'DOWN', or 'LEFT'.
        """
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        cell = self.grid[y][x]
        if direction == 'UP' and not (cell & 1):
            return True
        if direction == 'RIGHT' and not (cell & 2):
            return True
        if direction == 'DOWN' and not (cell & 4):
            return True
        if direction == 'LEFT' and not (cell & 8):
            return True
        return False

    def get_center_coord(self) -> tuple[int, int]:
        cx = (self.width - 1) // 2
        cy = (self.height - 1) // 2
        return (cx, cy)
