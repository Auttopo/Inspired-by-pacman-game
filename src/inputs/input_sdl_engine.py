
import sys
import random
from typing import Any, Callable, Generator
try:
    import ctypes
    import io
    import numpy as np
    from PIL import Image

    import sdl2 as s2
except ImportError as e:
    print(f"Error : missing library ({e.name}).")
    print("Solution : lunch 'make run'.")
    sys.exit(1)

from engine.engine import GameEngine
from inputs.init_input_engine import InitInputEngine


def limit_fps(start_frame: int, limit: int) -> None:
    """
    Limits the frame rate to ensure the game runs at a consistent speed.
    Delays the execution if the frame was rendered
    faster than the target time."""
    ticks = s2.SDL_GetTicks()

    if start_frame + limit > ticks:
        # TOO EARLY
        s2.SDL_Delay(start_frame + limit - ticks)


def void_func(*args: Any, **kwargs: Any) -> str:
    """
    A placeholder/dummy function used to ignore specific
    inputs in certain states.
    For example, ignoring keyboard inputs while in the menu."""
    return ""


def get_video_data(renderer: Any, w: int, h: int) -> bytes:

    pixels = ctypes.create_string_buffer(w * h * 4)
    ret = s2.SDL_RenderReadPixels(
                            renderer, None,
                            s2.SDL_PIXELFORMAT_RGBA32,
                            pixels, w * 4)
    if ret != 0:
        raise Exception("RenderReadPixels failded")
    arr = np.frombuffer(pixels, dtype=np.uint8).reshape(h, w, 4)
    img = Image.fromarray(arr, "RGBA").convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=70)
    return buf.getvalue()


class SDLCoreEngine(InitInputEngine):
    """
    The core engine responsible for running the game loop and state machine.
    Inherits initialized SDL2 components from InitInputEngine and orchestrates
    the transitions between the menu, gameplay, pause, and end screens.
    """

    def process_core_while(self) -> Generator[bytes, None, None]:
        """
        The main state machine of the game.
        Loops indefinitely until the 'exit' command is received. It sets up
        the appropriate input handlers, display functions, and background music
        for the current state"""
        game = True

        res = "menu"
        mouse_event = self.menu_mouse
        key_event = void_func
        display = self.d.display_menu
        self.s.set_background_sound("menu_sound")
        while game:
            if res != "confirm_quit":
                self.previous = res
            gen = self.core_while(
                    mouse_event,
                    key_event,
                    display
                    )
            try:
                while 1:
                    yi = next(gen)
                    yield yi
            except StopIteration as e:
                ret = e
            if res == "confirm_quit":
                if self.previous not in {"menu", "escape", "end"}:
                    res = "menu"

            self.text_mode = False
            self.d.text = ""
            match res:
                case "exit":
                    self.mutex.release()
                    return
                case "menu":
                    self.s.set_background_sound("menu_sound")
                    if self.previous not in {"instructions", "scores", "menu"}:
                        self.d.rotasprit = 1
                        self.d.rotadeath = -0.1
                    mouse_event = self.menu_mouse
                    key_event = void_func
                    display = self.d.display_menu
                case "newgame" | "reload":
                    self.s.set_background_sound("game_sound")
                    mouse_event = void_func
                    key_event = self.newgame_keys
                    display = self.d.display_and_compute_game
                    if self.previous != "escape":
                        if res != "reload":
                            print("\nStarting new game")
                            self.engine = GameEngine(self.config_path)
                        self.player = self.engine.player
                        self.d.engine = self.engine
                        self.d.init_engine(self.engine.score)
                        self.set_cell_size(
                            self.midxy[0] * 2, self.midxy[1] * 2)
                case "escape":
                    self.s.halt_background_sound()
                    mouse_event = self.escape_mouse
                    key_event = void_func
                    display = self.d.display_escape
                case "instructions":
                    mouse_event = self.instructions_mouse
                    key_event = void_func
                    display = self.d.display_instructions
                case "scores":
                    self.d.seed = random.randint(0, 10000)
                    mouse_event = self.instructions_mouse
                    key_event = void_func
                    display = self.d.display_scores
                case "confirm_quit":
                    mouse_event = self.confirm_quit_mouse
                    key_event = void_func
                    display = self.d.display_confirm_quit
                case "end":
                    self.d.text = ""
                    self.text_mode = True
                    mouse_event = self.end_mouse
                    key_event = self.end_keys
                    display = self.d.display_end

    def core_while(
                self,
                mousebuttonup: Callable[..., str],
                keydown: Callable[..., str],
                display:  Callable[..., str]
                ) -> Generator[bytes, None, str]:
        """
        The frame-by-frame execution loop for the current game state.
        Polls for SDL2 events (window resize, quit, mouse, keyboard, text)"""

        game = True

        fps_limit = self.fps_limit
        while game:
            self.mutex.acquire()

            start_frame = s2.SDL_GetTicks()

            event = s2.SDL_Event()
            while s2.SDL_PollEvent(event):
                match event.type:
                    case s2.SDL_QUIT:
                        return "exit"
                    case s2.SDL_WINDOWEVENT:
                        if event.window.event == s2.SDL_WINDOWEVENT_RESIZED:
                            w = event.window.data1
                            h = event.window.data2
                            self.midxy[0] = int(w / 2)
                            self.midxy[1] = int(h / 2)
                            self.width = w
                            self.height = h
                            self.set_cell_size(w, h)

                    case s2.SDL_MOUSEBUTTONUP:
                        res = mousebuttonup(event)
                        if res:
                            return res
                    case s2.SDL_KEYDOWN:
                        res = keydown(event)
                        if res:
                            return res
                    case s2.SDL_TEXTINPUT:
                        if self.text_mode:
                            self.d.text += event.text.text.decode()
                            if len(self.d.text) > 25:
                                self.d.text = ""
                                self.text_mode = False

            res = display()
            limit_fps(start_frame, fps_limit)
            if res:
                return res
            self.mutex.release()
            yield get_video_data(self.renderer, self.width, self.height)
        return ""
