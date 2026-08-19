
import sys
from typing import Any
try:
    import sdl2 as s2
except ImportError as e:
    print(f"Error : missing library ({e.name}).", file=sys.stderr)
    print("Solution : lunch 'make run'.", file=sys.stderr)
    sys.exit(1)

from engine.player import Direction
from inputs.init_input_engine import InitInputEngine


class InputProcesses(InitInputEngine):
    """
    Processes raw SDL2 events and translates them into game actions.
    Inherits from InitInputEngine to access the game engine,
    display coordinates, and sound manager."""

    def cheat_codes(self) -> str:
        """Parses text input commands entered by the user during gameplay.
        Activates invincibility & speed boost, or skips to the next level."""
        match self.d.text:
            case "/cheat":
                self.text_mode = False
                self.player.speed = self.player.speed * 1.25
                if self.player.speed > 1:
                    self.player.speed = 1
                if not self.engine.cheat_invincible:
                    self.engine.toggle_invincibility()
            case "/slow":
                self.player.speed -= 0.01
            case "/speed":
                self.player.speed = 0.1
            case "/next":
                self.text_mode = False
                if self.engine.current_level != 10:
                    self.engine.cheat_next_level()
                    return "reload"
        return ""

    def newgame_keys(self, event: Any) -> str:
        """
        Handles keyboard inputs during active gameplay.
        Processes directional movement (WASD/Arrows), opening the pause menu,
        and initiating the text input mode for cheat codes."""

        match event.key.keysym.sym:
            case s2.SDLK_UP | s2.SDLK_w:
                self.player.next_direction = Direction.UP
                if not self.d.start:
                    self.d.start = True
            case s2.SDLK_RIGHT | s2.SDLK_d:
                self.player.next_direction = Direction.RIGHT
                if not self.d.start:
                    self.d.start = True
            case s2.SDLK_DOWN | s2.SDLK_s:
                self.player.next_direction = Direction.DOWN
                if not self.d.start:
                    self.d.start = True
            case s2.SDLK_LEFT | s2.SDLK_a:
                self.player.next_direction = Direction.LEFT
                if not self.d.start:
                    self.d.start = True
            case s2.SDLK_ESCAPE:
                return "escape"
            case s2.SDLK_SLASH:
                self.text_mode = True
                self.d.text = ""
            case s2.SDLK_RETURN:
                res = self.cheat_codes()
                if res:
                    return res

        return ""

    def menu_mouse(self, event: Any) -> str:
        """
        Handles mouse clicks on the Main Menu screen."""

        if event.button.button == s2.SDL_BUTTON_LEFT:
            act = self.check_button(
                                    event.button.x,
                                    event.button.y)
            if act:
                return act
        return ""

    def get_menu_buttons(self) -> dict[str, Any]:
        """
        Calculates the bounding boxes (Left-Up to Right-Down coordinates)
        for all buttons on the Main Menu dynamically based on screen size."""
        data = dict()

        jump = 350
        w = int(self.midxy[1] / 2)
        h = int(self.midxy[1] / 4)
        pading = int(w / 2)

        x_lu = self.midxy[0] - w / 2  # left up
        x_rd = self.midxy[0] + w / 2  # right down

        y_lu = jump + pading
        y_rd = y_lu + h
        inside = {"lu": (x_lu, y_lu), "rd": (x_rd, y_rd)}
        data.update({"newgame": inside})

        y_lu = jump + pading * 2
        y_rd = y_lu + h
        inside = {"lu": (x_lu, y_lu), "rd": (x_rd, y_rd)}
        data.update({"scores": inside})

        y_lu = jump + pading * 3
        y_rd = y_lu + h
        inside = {"lu": (x_lu, y_lu), "rd": (x_rd, y_rd)}
        data.update({"instructions": inside})

#        y_lu = jump + pading * 4
#        y_rd = y_lu + h
#        inside = {"lu": (x_lu, y_lu), "rd": (x_rd, y_rd)}
#        data.update({"confirm_quit": inside})

        return data

    def check_button(self, x: int, y: int) -> str:
        """
        Checks if a given (x, y) coordinate falls within any of the main menu
        button hitboxes or the music toggle button."""
        button = self.get_menu_buttons()
        self.set_music_off(x, y)
        for option in button.keys():
            if button[option]['lu'][0] < x < button[option]['rd'][0]:
                if button[option]['lu'][1] < y < button[option]['rd'][1]:
                    return str(option)
        return ""

    def set_music_off(self, x: int, y: int) -> str:
        """
        Toggles the background music state if the coordinates fall within
        the music icon's bounding box."""
        lux = 25
        luy = self.midxy[1] * 2 - 175
        size = 150
        if lux < x < lux + size:
            if luy < y < luy + (size):
                if self.s.music_off:
                    self.s.music_off_background_sound(False)
                else:
                    self.s.music_off_background_sound(True)
        return ""

    def return_menu(self, event: Any) -> str:
        """
        Checks if the 'Return to Menu' button (top-left corner) was clicked."""

        size = 190
        ypad = 90
        lux = int(self.midxy[0] / 10)
        luy = int(self.midxy[1] / 10)
        if lux < event.button.x < lux + size:
            if luy < event.button.y < luy + (size - ypad):
                return "confirm_quit"
        return ""

    def escape_mouse(self, event: Any) -> str:
        """
        Handles mouse clicks on the Pause/Escape screen.
        Can resume the game, toggle music, or attempt to return to the menu."""
        self.set_music_off(event.button.x, event.button.y)
        if event.button.button == s2.SDL_BUTTON_LEFT:
            size = 600
            ypad = 300
            lux = int(self.midxy[0] - size / 2)
            luy = int(self.midxy[1] - (size - ypad + 100) / 2)
            if lux < event.button.x < lux + size:
                if luy < event.button.y < luy + (size - ypad):
                    return "newgame"

            ret = self.return_menu(event)
            if ret:
                return ret
        return ""

    def instructions_mouse(self, event: Any) -> str:
        """
        Handles mouse clicks on the Instructions screen."""

        if event.button.button == s2.SDL_BUTTON_LEFT:
            ret = self.return_menu(event)
            if ret:
                return ret
        return ""

    def confirm_quit_mouse(self, event: Any) -> str:
        """
        Handles mouse clicks on the 'Are You Sure?' confirmation dialog.
        Saves the high score if the player is quitting an active game."""

        if event.button.button == s2.SDL_BUTTON_LEFT:

            sizex = 800
            sizey = 400
            gapx = 30
            gapy = 60
            lux = self.midxy[0] - 400
            luy = self.midxy[1] - 170

            if lux + gapx < event.button.x < lux + sizex - gapx:
                if luy + gapy < event.button.y < luy + sizey - gapy:
                    if event.button.x < self.midxy[0] - 110:
                        return str(self.previous)
                    if event.button.x > self.midxy[0] + 110:
                        if self.d.name:
                            self.engine.highscore_manager.add_score(
                                                            self.d.name,
                                                            self.engine.score)
                            self.d.name = ""
                        if self.previous == "menu":
                            return "exit"
                        else:
                            return "menu"
        return ""

    def end_mouse(self, event: Any) -> str:
        """
        Handles mouse clicks on the Game Over / Victory screen.
        (Currently unused, reserved for future UI additions).
        """
        return ""

    def end_keys(self, event: Any) -> str:
        """
        Handles keyboard inputs on the Game Over / Victory screen,
        specifically for entering the player's name
        into the high score list."""

        match event.key.keysym.sym:
            case s2.SDLK_BACKSPACE:
                self.d.text = self.d.text[:-1]
            case s2.SDLK_RETURN:
                if self.d.text and len(self.d.text) <= 10 and \
                        self.d.text.isalnum():
                    self.d.name = self.d.text
                    return "confirm_quit"
        return ""
