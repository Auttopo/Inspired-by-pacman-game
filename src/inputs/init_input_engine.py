
import sys
from enum import IntEnum
from typing import Any
try:
    import sdl2 as s2
    import sdl2.sdlttf as s2_ttf
    import sdl2.sdlmixer as s2_mix
except ImportError as e:
    print(f"Error : missing library ({e.name}).")
    print("Solution : lunch 'make run'.")
    sys.exit(1)

from engine.engine import GameEngine
from display.helpers.textures import Textures
from display.helpers.sounds import Sounds
from display.display import Display


class D(IntEnum):  # DEFAULT
    """
    Default configuration constants for the game window.
    Defines the initial width (w) and height (h) in pixels.
    """

    w = 1200
    h = 900


class InputError(Exception):
    """
    Custom exception raised when an SDL2 subsystem, window, or renderer
    fails to initialize properly.
    """
    pass


class InitInputEngine:
    """
    Bootstraps the game environment.
    Initializes the GameEngine, loads SDL2 libraries (fonts, mixer, textures),
    creates the application window, and links everything to the Display facade.
    Handles graceful degradation
    """

    def __init__(self, path: str) -> None:
        """
        Initializes the setup engine with basic configurations."""

        self.fps_limit = 16  # 1000 ms / 60 frames = 16.666 fps
        self.midxy: list[int] = [int(D.w / 2), int(D.h / 2)]
        self.config_path = path
        self.engine = GameEngine(path)
        self.sounds: dict[str, Any] = dict()
        self.s = Sounds()
        self.player = self.engine.player
        self.previous = ""
        self.text_mode = False

    def init_game(self) -> None:
        """
        The main initialization sequence.
        Starts SDL2, TTF, and Mixer. Loads custom fonts and audio chunks.
        Creates the main resizable window and the hardware-accelerated
        renderer"""

        check = s2.SDL_Init(s2.SDL_INIT_VIDEO | s2.SDL_INIT_AUDIO)
        if check != 0:
            raise InputError("Error. Can't init SDL2")

        if s2_ttf.TTF_Init() != 0:
            s2.SDL_Quit()
            raise InputError("Error. Can't init SDL_TTF")
        try:
            self.font1 = s2_ttf.TTF_OpenFont(b"assets/MoonAndLatte-vn8LO.ttf",
                                             50)
            if not self.font1:
                raise InputError("can't load font")
            self.font2 = s2_ttf.TTF_OpenFont(b"assets/Shirtsy-8Z2A.ttf",
                                             50)
            if not self.font2:
                s2_ttf.TTF_CloseFont(self.font1)
                raise InputError("can't load font")
            self.font3 = s2_ttf.TTF_OpenFont(
                                            b"assets/Brookeshappell8-eoKB.ttf",
                                            50)
            if not self.font3:
                s2_ttf.TTF_CloseFont(self.font1)
                s2_ttf.TTF_CloseFont(self.font2)
                raise InputError("can't load font")
        except Exception:
            s2_ttf.TTF_Quit()
            s2.SDL_Quit()
            raise

        check = s2_mix.Mix_OpenAudio(44100, s2_mix.MIX_DEFAULT_FORMAT, 2, 2028)
        if check != 0:
            self.close_fonts()
            s2.SDL_Quit()
        try:
            self.s.load_sounds()
            self.sounds = self.s.sounds
        except Exception:
            self.s.free_all_sounds()
            self.close_fonts()
            s2.SDL_Quit()
            raise

        self.window = s2.SDL_CreateWindow(
                                        b"Pacman",
                                        s2.SDL_WINDOWPOS_CENTERED,
                                        s2.SDL_WINDOWPOS_CENTERED,
                                        D.w, D.h,
                                        s2.SDL_WINDOW_SHOWN |
                                        s2.SDL_WINDOW_RESIZABLE)
        if not self.window:
            self.close_fonts()
            self.s.free_all_sounds()
            s2.SDL_Quit()
            raise InputError("Error. Can't init window")
        s2.SDL_SetWindowMinimumSize(self.window, D.w, D.h)

        try:
            self.renderer = s2.SDL_CreateRenderer(
                    self.window,
                    -1,
                    s2.SDL_RENDERER_ACCELERATED
            )
        except Exception:
            print("can't load gpu, loading on cpu")
            self.renderer = s2.SDL_CreateRenderer(
                    self.window,
                    -1,
                    s2.SDL_RENDERER_SOFTWARE
            )
        if not self.renderer:
            self.close_fonts()
            s2.SDL_DestroyWindow(self.window)
            self.s.free_all_sounds()
            s2.SDL_Quit()
            raise InputError("Error. Can't init renderer")
        s2.SDL_SetRenderDrawColor(self.renderer, 62, 98, 124, 255)

        try:
            self.textures = Textures(self.renderer)
            self.t = self.textures.load_textures()
            self.d = Display(self.engine, self.fps_limit,
                             self.renderer, self.s, self.t,
                             self.font1, self.font2, self.font3,
                             self.midxy)
            self.set_cell_size(D.w, D.h)
        except Exception:
            self.free_all()
            raise
        print("Game loaded correcly")

    def set_cell_size(self, w: int, h: int) -> None:
        """
        Dynamically calculates the pixel size of each grid cell based on the
        current window dimensions and the maze size."""
        pad = 250
        ref_x = int((w - pad) / len(self.d.maze[0]))
        ref_w = int((h - pad) / len(self.d.maze))
        if ref_x < ref_w:
            self.d.cell = ref_x
        else:
            self.d.cell = ref_w

        if self.d.cell < 50:
            self.d.cell = 80
            self.d.pov_rpg = True
        else:
            self.d.pov_rpg = False

    def free_all(self) -> None:
        """
        Safely destroys all SDL2 resources (textures, renderer, fonts, audio)
        to prevent memory leaks upon exiting the game.
        """
        self.close_fonts()
        self.textures.destroy_all()
        s2.SDL_DestroyRenderer(self.renderer)
        s2.SDL_DestroyWindow(self.window)
        self.s.free_all_sounds()
        s2.SDL_Quit()
        self.end_safe = True

    def close_fonts(self) -> None:
        """
        Helper method to close all loaded TTF fonts and shut down the
        SDL_ttf subsystem cleanly.
        """
        s2_ttf.TTF_CloseFont(self.font1)
        s2_ttf.TTF_CloseFont(self.font2)
        s2_ttf.TTF_CloseFont(self.font3)
        s2_ttf.TTF_Quit()
