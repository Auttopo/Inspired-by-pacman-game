
import sdl2.sdlmixer as s2_mix
import sdl2 as s2
import time
import random

from engine.ghost import GhostState
from engine.player import Direction
from display.display_base import BaseDisplay


class DisplayGame(BaseDisplay):
    """
    Renders the active gameplay screen and synchronizes visual updates
    with the underlying GameEngine."""

    rotasprit: float | int
    sprits_rate: float
    n_rotasprit: int
    score_trace: int
    shake_death: float
    end: bool
    start: bool
    # rotadeath: float | int
    # text: str
    # i: int

    def draw_pacman(self, padx: int, pady: int) -> None:
        """
        Renders the Pac-Man sprite based on his current direction
        and animation frame. Also switches to a special texture
        if the invincibility cheat is active. """
        if self.engine.cheat_invincible:
            skin = "sprit_pacman_cheat"
        else:
            skin = "sprit_pacman"
        match self.player.next_direction:
            case Direction.UP:
                self.row = 0
            case Direction.LEFT:
                self.row = 2
            case Direction.RIGHT:
                self.row = 3
            case Direction.DOWN:
                self.row = 1
            case _:
                col = self.rotasprit
                w, h = 250, 250
                src = s2.SDL_Rect(2 * w, self.row * h, w, h)
                dst = s2.SDL_Rect(int(self.player.xf * self.cell + padx),
                                  int(self.player.yf * self.cell + pady),
                                  self.cell, self.cell)
                s2.SDL_RenderCopy(self.renderer, self.t[skin], src, dst)
                return
        col = self.rotasprit
        w, h = 250, 250
        src = s2.SDL_Rect(col * w, self.row * h, w, h)
        dst = s2.SDL_Rect(int(self.player.xf * self.cell + padx),
                          int(self.player.yf * self.cell + pady),
                          self.cell, self.cell)
        s2.SDL_RenderCopy(self.renderer, self.t[skin], src, dst)

    def draw_ghosts(self, padx: int, pady: int) -> None:
        """
        Renders all active ghosts. Applies color modulations (flashing)
        if the ghosts are in the EDIBLE state.  """

        for i, ghost in enumerate(self.ghosts):

            color = self.ghost_color[ghost.color_id]
            match ghost.direction:
                case "UP":
                    row = 0
                case "LEFT":
                    row = 2
                case "RIGHT":
                    row = 3
                case _:
                    row = 1
            if ghost.state == GhostState.EDIBLE:
                if ghost.timer <= 2 and self.rotasprit > 3:
                    s2.SDL_SetTextureColorMod(self.t[color], 198, 120, 235)
                else:
                    s2.SDL_SetTextureColorMod(self.t[color], 110, 80, 220)
            else:
                s2.SDL_SetTextureColorMod(self.t[color], 255, 255, 255)
            if ghost.state == GhostState.DEAD:
                if ghost.timer > 2:
                    s2.SDL_SetTextureAlphaMod(self.t[color], 0)
                elif self.rotasprit > 3:
                    s2.SDL_SetTextureAlphaMod(self.t[color], 170)
                else:
                    s2.SDL_SetTextureAlphaMod(self.t[color], 120)
            else:
                s2.SDL_SetTextureAlphaMod(self.t[color], 255)

            col = ghost.rotasprit
            w, h = 250, 250
            src = s2.SDL_Rect(col * w, row * h, w, h)
            dst = s2.SDL_Rect(int(ghost.xf * self.cell + padx),
                              int(ghost.yf * self.cell + pady),
                              self.cell, self.cell)
            s2.SDL_RenderCopy(self.renderer, self.t[color], src, dst)

    def draw_infos(self) -> None:
        """
        Renders the Heads-Up Display (HUD) including the current score,
        remaining lives, level number, and countdown timer.  """

        s_score = f"{self.engine.score}"
        self.draw_text(s_score, self.midxy[0] - 20, 15, len(s_score) * 20,
                       50, self.font1, "orange")

        dst = s2.SDL_Rect(self.midxy[0] - 200, 5, 165, 70)
        s2.SDL_RenderCopy(self.renderer, self.t["score"], None, dst)

        dst = s2.SDL_Rect(int(self.midxy[0] / 6 - 100), 150, 160, 70)
        s2.SDL_RenderCopy(self.renderer, self.t["lives"], None, dst)

        dst = s2.SDL_Rect(int(self.midxy[0] / 3), -10, 130, 100)
        s2.SDL_RenderCopy(self.renderer, self.t["level"], None, dst)
        s_level = f"{self.engine.current_level}"
        self.draw_text(s_level, int(self.midxy[0] / 3) + 140, 0,
                       len(s_level) * 50, 80, self.font2, "blue")

        dst = s2.SDL_Rect(self.midxy[0] - 400,
                          self.midxy[1] * 2 - 150, 420, 140)
        s2.SDL_RenderCopy(self.renderer, self.t["time"], None, dst)
        if self.engine.time_left < 0:
            self.engine.time_left = 0
        s_time = f"{round(self.engine.time_left, 2)}"
        self.draw_text(s_time, self.midxy[0] + 30, self.midxy[1] * 2 - 105,
                       len(s_time) * 20, 50, self.font1, "white")

        if self.player.lives < 4:
            col = self.player.lives - 1
            row = 0
            w, h = 150, 300
            src = s2.SDL_Rect(col * w, row * h, w, h)
            dst = s2.SDL_Rect(int(self.midxy[0] / 6) + 40, 135, 100, 130)
            s2.SDL_RenderCopy(self.renderer, self.t['sprit_lives'], src, dst)
        else:
            self.draw_text(
                    f"{self.player.lives}",
                    int(self.midxy[0] / 6) + 40, 135, 100, 130,
                    self.font1,
                    "purple"
            )

    def rotate_all_sprits(self) -> None:
        """
        Updates the animation frames for Pac-Man and all ghosts, creating
        the illusion of movement by cycling through sprite sheet columns."""
        if self.sprits_rate == 0:
            for ghost in self.ghosts:
                ghost.rotasprit = (ghost.rotasprit + 1) % 5
            self.n_rotasprit -= 1
            if self.n_rotasprit == -6:
                self.n_rotasprit = 4
            self.rotasprit = abs(self.n_rotasprit)

        self.sprits_rate = (self.sprits_rate + 1) % 5

        if self.player.xf == self.xyf[0] and self.player.yf == self.xyf[1]:
            self.player.next_direction = Direction.NONE
        self.xyf[0] = self.player.xf
        self.xyf[1] = self.player.yf

    def game_over_process(self, padx: int, pady: int) -> str:
        """
        Plays the Game Over death animation and sound, blocking further input
        until the sequence is finished."""

        self.sprits_rate -= 0.5
        if self.rotadeath < 6.1:
            self.rotadeath += 0.1
            row = int(self.rotadeath)
        else:
            row = 7

        w, h = 600, 250
        src = s2.SDL_Rect(0, row * h, w, h)
        dst = s2.SDL_Rect(int(self.player.xf * self.cell + padx),
                          int(self.player.yf * self.cell + pady),
                          round(self.cell / 250 * 600), self.cell)
        s2.SDL_RenderCopy(self.renderer,
                          self.t["sprit_pacman_death"], src, dst)

        msg = "GAME   OVER"
        w = int(110 * len(msg))
        h = 500
        x = int(self.midxy[0] - w / 2)
        y = int(self.midxy[1] - h / 2)
        self.draw_text(msg, x, y, w, h, self.font2, "black")

        if not self.end:
            self.s.set_background_sound("death_sound", 0)
            self.end = True
            self.winned = False
            self.time = time.time()
        now = time.time()
        if now - self.time > 5:
            return "end"
        return ""

    def game_win_process(self, padx: int, pady: int) -> str:
        """
        Plays the Victory animation and sound upon successfully completing
        all levels. Blocks input during the sequence."""

        self.sprits_rate -= 0.5
        if self.rotadeath < 4.1:
            self.rotadeath += 0.1
            col = int(self.rotadeath)
        else:
            col = 5

        w, h = 250, 250
        src = s2.SDL_Rect(col * w, 2 * h, w, h)
        dst = s2.SDL_Rect(int(self.player.xf * self.cell + padx),
                          int((
                              self.player.yf - self.rotadeath * 2 / 10
                              ) * self.cell + pady),
                          self.cell, self.cell)
        s2.SDL_RenderCopyEx(self.renderer, self.t["sprit_pacman"], src, dst,
                            self.rotadeath * 2, None, s2.SDL_FLIP_NONE)

        msg = "YOU   WIN"
        w = int(110 * len(msg))
        h = 500
        x = int(self.midxy[0] - w / 2)
        y = int(self.midxy[1] - h / 2)
        self.draw_text(msg, x, y, w, h, self.font2, "green")

        if not self.end:
            self.s.set_background_sound("win_sound", 0)
            self.end = True
            self.winned = True
            self.time = time.time()
        now = time.time()
        if now - self.time > 5:
            return "end"
        return ""

    def display_and_compute_game(self) -> str:
        """
        The main rendering loop iteration. Clears the screen, updates the game
        engine, manages camera movements (RPG mode or screen shake),
        draws all entities (maze, player, ghosts, HUD),
        and presents the final frame.  """

        s2.SDL_RenderClear(self.renderer)

        # DISABLED TO SAVE RESOURCES
        #if self.score_trace != self.engine.score:
        #    s2_mix.Mix_PlayChannel(
        #                        -1,
        #                        self.sounds[random.choice(self.eat_sounds)],
        #                        0)

        self.score_trace = self.engine.score

        lives = self.player.lives
        level = self.engine.current_level
        if self.shake_death == 0:
            if self.start:
                self.engine.update(self.delta_time)
                if level != self.engine.current_level:
                    return "reload"
        else:
            if self.midxy[0] <= self.shake_death:
                self.midxy[0] -= 2
            else:
                self.midxy[0] += 2
            if self.midxy[0] == self.shake_death - 12:
                self.midxy[0] = self.shake_death + 1

            if self.midxy[0] == self.shake_death + 11:
                self.midxy[0] = self.shake_death
                self.shake_death = 0

        if self.player.lives != lives:
            self.start = False
            self.shake_death = self.midxy[0]
            
            # DISABLED TO SAVE RESOURCES
            # s2_mix.Mix_PlayChannel(-1, self.sounds["left_life_sound"], 0)


        if self.pov_rpg:
            player_distx_0 = (self.cell * self.player.xf + self.cell / 2)
            player_disty_0 = (self.cell * self.player.yf + self.cell / 2)
            startx = int(self.midxy[0] - player_distx_0)
            starty = int(self.midxy[1] - player_disty_0)
            posy = starty
        else:
            startx = int(self.midxy[0] - len(self.maze[0]) / 2 * self.cell)
            starty = 90
            posy = starty

        half_wall = int(self.cell / 10)
        mazeleny = len(self.maze)
        mazelenx = len(self.maze[0])

        for y in range(mazeleny):
            posx = startx
            # draw full-west wall
            dst = s2.SDL_Rect(
                    startx - half_wall, posy, half_wall * 2, self.cell)
            s2.SDL_RenderCopy(self.renderer, self.t["wall"], None, dst)

            for x in range(mazelenx):
                # draw full-north wall
                dst = s2.SDL_Rect(
                                posx, starty - half_wall,
                                self.cell, half_wall * 2)
                s2.SDL_RenderCopy(self.renderer, self.t["wall"], None, dst)

                # 1. draw east and south walls
                cell_wall = self.maze[y][x]
                if cell_wall == 15:
                    dst = s2.SDL_Rect(posx, posy, self.cell, self.cell)
                    s2.SDL_RenderCopy(self.renderer, self.t["wall"], None, dst)
                else:
                    # 2 = East, 4 = South
                    if cell_wall & 2 \
                        and (
                            x + 1 == mazelenx or self.maze[y][x + 1] != 15):
                        dst = s2.SDL_Rect(
                                        posx + self.cell - half_wall,
                                        posy, half_wall * 2, self.cell)
                        s2.SDL_RenderCopy(
                                        self.renderer, self.t["wall"],
                                        None, dst)
                    if cell_wall & 4 and \
                            (y + 1 == mazeleny or self.maze[y + 1][x] != 15):
                        dst = s2.SDL_Rect(
                                        posx, posy + self.cell - half_wall,
                                        self.cell, half_wall * 2)
                        s2.SDL_RenderCopy(
                                        self.renderer,
                                        self.t["wall"], None, dst)

                # 2. draw items
                match self.engine.maze.items[y][x]:
                    case 2:  # PACGUM
                        dst = s2.SDL_Rect(posx, posy, self.cell, self.cell)
                        s2.SDL_RenderCopy(
                                        self.renderer, self.t["pacgum"],
                                        None, dst)

                    case 3:  # SUPERPACGUM
                        if self.rotasprit > 3:
                            s2.SDL_SetTextureColorMod(self.t["megapacgum"],
                                                      255, 240, 100)
                        elif self.rotasprit == 3:
                            s2.SDL_SetTextureColorMod(self.t["megapacgum"],
                                                      255, 247, 202)
                        else:
                            s2.SDL_SetTextureColorMod(self.t["megapacgum"],
                                                      255, 255, 255)
                        dst = s2.SDL_Rect(posx, posy, self.cell, self.cell)
                        s2.SDL_RenderCopy(self.renderer, self.t["megapacgum"],
                                          None, dst)

                posx += self.cell
            posy += self.cell

        padx = startx - self.cell / 2
        pady = starty - self.cell / 2
        self.draw_ghosts(padx, pady)
        if self.engine.is_game_over or self.engine.is_victory:
            if self.engine.is_victory:
                end = self.game_win_process(padx, pady)
            else:
                end = self.game_over_process(padx, pady)
            if end:
                self.draw_infos()
                self.rotate_all_sprits()
                s2.SDL_RenderPresent(self.renderer)
                return end
        else:
            self.draw_pacman(padx, pady)
        self.draw_infos()
        self.rotate_all_sprits()
        s2.SDL_RenderPresent(self.renderer)
        return ""
