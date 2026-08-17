
import sdl2 as s2
import sdl2.sdlttf as s2_ttf
from typing import Any
import time
import random
from engine.engine import GameEngine
from display.helpers.sounds import Sounds


class DiplayError(Exception):
    """Custom exception raised for critical rendering or display errors."""
    pass


class BaseDisplay:
    """
    Base class for rendering the game interface and entities.
    Holds references to the game engine, textures, sounds, and fonts
    """

    def __init__(self, engine: GameEngine, fps_limit: int,
                 renderer: Any, sounds: Sounds, textures: dict[str, Any],
                 font1: Any, font2: Any, font3: Any, midxy: list[int]) -> None:
        """
        Initializes the base display components.  """
        self.engine = engine
        self.start = False
        self.s = sounds
        self.sounds = sounds.sounds
        self.eat_sounds = ["eat_sound1", "eat_sound2", "eat_sound3"]
        self.renderer = renderer
        self.t = textures
        self.shake_death = 0

        self.init_engine(self.engine.current_level)

        self.rotasprit: float | int = 1
        self.rotadeath: float | int = -0.1
        self.n_rotasprit: float | int = 4
        self.sprits_rate = 0
        self.time = time.time()
        self.end = False
        self.winned = False

        self.p_direction = ""
        self.delta_time = fps_limit / 1000
        self.font1 = font1
        self.font2 = font2
        self.font3 = font3
        self.midxy = midxy
        self.cell = 0
        self.pov_rpg = False
        self.text = ""
        self.score_trace = 1
        self.i = 0
        self.seed = 0
        self.xyf = [0, 0]
        self.row = 1
        self.name = ""
        self.ghost_color = {
            0: "sprit_ghost1",
            1: "sprit_ghost2",
            2: "sprit_ghost3",
            3: "sprit_ghost4",
        }
        self.txt_color = {
                        "white":  s2.SDL_Color(255, 255, 255, 255),
                        "black":  s2.SDL_Color(0, 0, 0, 255),
                        "red":    s2.SDL_Color(220, 20, 60, 255),
                        "yellow": s2.SDL_Color(255, 215, 0, 255),
                        "blue":   s2.SDL_Color(30, 144, 255, 255),
                        "pink":   s2.SDL_Color(255, 20, 147, 255),
                        "green":  s2.SDL_Color(50, 205, 50, 255),
                        "orange": s2.SDL_Color(255, 140, 0, 255),
                        "purple": s2.SDL_Color(150, 80, 210, 255),
                    }
        self.colors = [
                        "white",
                        "black",
                        "red",
                        "yellow",
                        "blue",
                        "pink",
                        "green",
                        "orange",
                        "purple",
        ]

    def init_engine(self, score: int) -> None:
        """
        Resets and synchronizes the display variables with the current state
        of the game engine when a new level or attempt starts.  """
        self.start = False
        self.i = 0
        self.maze = self.engine.maze.grid
        self.player = self.engine.player
        self.ghosts = self.engine.ghosts
        self.score_trace = score
        self.sprits_rate = 0
        self.rotasprit = 1
        self.rotadeath = -0.1
        if self.shake_death != 0:
            self.midxy[0] = self.shake_death
        self.shake_death = 0
        self.end = False
        self.xyf = [0, 0]
        self.row = 1
        for ghost in self.ghosts:
            ghost.rotasprit = random.randint(0, 4)

    def draw_text(self, string: str,
                  x: int, y: int,
                  w: int, h: int,
                  font: Any,
                  color: str) -> None:
        """Renders a given text string to the screen."""

        surface = s2_ttf.TTF_RenderText_Solid(font, string.encode('utf-8'),
                                              self.txt_color[color])
        texture = s2.SDL_CreateTextureFromSurface(self.renderer, surface)
        s2.SDL_FreeSurface(surface)
        dst = s2.SDL_Rect(x, y, w, h)
        s2.SDL_RenderCopy(self.renderer, texture, None, dst)
        s2.SDL_DestroyTexture(texture)
