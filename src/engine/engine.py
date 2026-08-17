from typing import List
# Assuming you have saved your previous classes in these files:
from engine.config import GameConfig
from engine.maze import Maze
from engine.player import Player
from engine.player import Direction
from engine.ghost import Ghost
from engine.ghost import GhostState
import math
from engine.highscore import HighscoreManager
import random


def update_pos(entity: Ghost | Player, pos: str, goal: float,
               speed: float) -> float:
    """ decrease position value"""
    rest = 0

    if pos == "x":
        if goal > entity.xf and goal < (entity.xf + speed):
            rest = (entity.xf + speed) - goal
            speed = speed - rest
        elif goal < entity.xf and goal > (entity.xf + speed):
            rest = goal - (entity.xf + speed)
            speed = speed + rest

        entity.xf = entity.xf + speed
        entity.x = int(entity.xf)
    else:
        if goal > entity.yf and goal < (entity.yf + speed):
            rest = (entity.yf + speed) - goal
            speed = speed - rest
        elif goal < entity.yf and goal > (entity.yf + speed):
            rest = goal - (entity.yf + speed)
            speed = speed + rest

        entity.yf = entity.yf + speed
        entity.y = int(entity.yf)

    return rest


def rail_movements(entity: Ghost | Player) -> None:
    """ move to a destination """

    # Use move method before use rail_movements

    move = True
    speed = entity.speed
    if entity.destx != -1:
        while move:
            midx = int(entity.xf) + 0.5
            midy = int(entity.yf) + 0.5
            xf = entity.xf
            yf = entity.yf
            desty = entity.desty
            destx = entity.destx
            dist_dest = math.sqrt(((destx - xf) ** 2)
                                  + ((desty - yf) ** 2))
            if dist_dest > 1 and (destx != xf or desty != yf):
                # we are not aligned, go to center of the case
                # the center is the shorter and mandatory passage to go dest
                if midx != xf:
                    if xf < midx:
                        speed = update_pos(entity, "x", midx, speed)
                    else:
                        speed = update_pos(entity, "x", midx, -speed)
                else:
                    if yf < midy:
                        speed = update_pos(entity, "y", midy, speed)
                    else:
                        speed = update_pos(entity, "y", midy, -speed)
                if speed == 0:
                    move = False
            elif dist_dest > 0:
                # we are aligned now go in line to the dest
                if destx != xf:
                    if xf < destx:
                        speed = update_pos(entity, "x", destx, speed)
                    else:
                        speed = update_pos(entity, "x", destx, -speed)
                else:
                    if yf < desty:
                        speed = update_pos(entity, "y", desty, speed)
                    else:
                        speed = update_pos(entity, "y", desty, -speed)
                if speed != 0:
                    entity.destx = -1
                move = False
            else:
                # we are arrived
                entity.destx = -1


class GameEngine:
    """
    The core engine that coordinates the Maze, Player, Ghosts, and Game Rules.
    """

    def __init__(self, config_path: str) -> None:
        """
        Loading the config and setting up level 1.
        """
        self.config: GameConfig = GameConfig(config_path)
        # Game Stats
        self.score: int = 0
        self.current_level: int = 1
        self.is_game_over: bool = False
        self.is_victory: bool = False
        # Game Entities
        self.maze: Maze
        self.player: Player
        self.ghosts: List[Ghost] = []
        self.cheat_invincible: bool = False
        hs_filename = self.config.settings.get("highscore_filename",
                                               "highscores.json")
        self.highscore_manager = HighscoreManager(hs_filename)
        self.player_died_event = False
        # Load the first level
        self.load_level()

    def load_level(self) -> None:
        """
        Generates the maze and places the player and ghosts for current level.
        """
        base_seed: int = self.config.settings.get("seed", 42)
        if self.current_level == 1:
            seed = base_seed
        else:
            random.seed()
            seed = random.randint(0, 100000)
        levels_config = self.config.settings.get("level",
                                                 [{"width": 21, "height": 21}])
        # SYSTEM de securite si on depasse level max donnee
        level_index = min(self.current_level - 1, len(levels_config) - 1)
        width: int = levels_config[level_index].get("width", 21)
        height: int = levels_config[level_index].get("height", 21)
        self.maze = Maze(width, height, seed)
        start_x, start_y = self.maze.get_center_coord()
        if self.maze.grid[start_y][start_x] == 1:
            start_x += 1
        #   PLACE PLAYER
        lives: int = self.config.settings.get("lives", 3)
        if self.current_level == 1:
            self.player = Player(start_x, start_y, lives)
        else:
            self.player.set_new_level_start(start_x, start_y)
        if self.current_level == 1:
            self.ghosts = [
                Ghost(0, 0, 0),                  # Top-Left
                Ghost(width - 1, 0, 1),          # Top-Right
                Ghost(0, height - 1, 2),         # Bottom-Left
                Ghost(width - 1, height - 1, 3)  # Bottom-Right
            ]
        else:
            self.ghosts[0].reset_for_new_level(0, 0)
            self.ghosts[1].reset_for_new_level(width - 1, 0)
            self.ghosts[2].reset_for_new_level(0, height - 1)
            self.ghosts[3].reset_for_new_level(width - 1, height - 1)
        empty_cells = width * height
        self.time_left = float(empty_cells / 1.4)

    def _move_player(self) -> None:
        """
        Handles Pac-Man's movement on the grid and wall collisions.
        """
        # We test the directions in order:'next' one, then 'current' one
        directions_to_try = [self.player.next_direction,
                             self.player.current_direction]
        for direction in directions_to_try:
            if direction == Direction.NONE:
                continue
            # If the desired cell is not a wall, we move!
            if self.maze.can_move(self.player.x, self.player.y,
                                  direction.name):
                dx, dy = direction.value
                self.player.current_direction = direction
                self.player.destx = self.player.x + dx + 0.5
                self.player.desty = self.player.y + dy + 0.5
                return
        # If both directions blocked by walls We stop
        self.player.current_direction = Direction.NONE

    def toggle_invincibility(self) -> None:
        """ Activate or desactivate cheat mode."""
        self.cheat_invincible = not self.cheat_invincible

    def cheat_next_level(self) -> None:
        """pass to next level"""
        if self.current_level < 10:
            self.current_level += 1
            self.load_level()
            print(f"CHEAT : Passage au niveau {self.current_level} !")

    def _check_collisions(self) -> None:
        """
        Checks for collisions between Pac-Man, pacgums, and ghosts.
        """
        # We store the player's position
        px = self.player.x
        py = self.player.y
        # Look at what is on the ground at Pac-Man's exact location
        current_item = self.maze.items[py][px]
        if current_item == 2:
            # Pac-Man ate a normal pacgum
            self.score += self.config.settings.get("points_per_pacgum", 10)
            self.maze.items[py][px] = 0
        elif current_item == 3:
            # Pac-Man ate a Super-pacgum
            for ghost in self.ghosts:
                ghost.destx = -1
            self.score += self.config.settings.get("points_per_super_pacgum",
                                                   50)
            self.maze.items[py][px] = 0
            # Make all ghosts edible!
            for ghost in self.ghosts:
                ghost.set_edible()

        self._hit_box_process(self.player.xf, self.player.yf)

    def _hit_box_process(self, pxf: float, pyf: float) -> None:
        """ check hit box collisions with precise positions"""

        def hit_box_tolerence(ghost: Ghost, pxf: float, pyf: float) -> bool:
            tolerence = 0.5
            if tolerence > ghost.xf - pxf > - tolerence:
                if tolerence > ghost.yf - pyf > - tolerence:
                    return True
            return False

        # GHOST COLLISIONS
        for ghost in self.ghosts:
            if ghost.state == GhostState.DEAD:
                continue
            # If Pac-Man and a Ghost are on the exact same tile
            if hit_box_tolerence(ghost, pxf, pyf):
                if self.cheat_invincible:
                    ghost.die()
                elif ghost.state == GhostState.EDIBLE:
                    # Pac-Man eats the ghost!<
                    self.score += self.config.settings.get("points_per_ghost",
                                                           200)
                    ghost.die()
                elif ghost.state == GhostState.CHASE:
                    if not self.cheat_invincible:
                        # The ghost eats Pac-Man!
                        self.player.lose_life()
                        self.player_died_event = True
                    # we reset ghosts to their corners
                    for g in self.ghosts:
                        g.x = g.start_x
                        g.y = g.start_y
                        g.xf = g.start_x + 0.5
                        g.yf = g.start_y + 0.5
                        g.destx = -1
                        g.desty = 0
                        g.direction = "DOWN"
                        g.state = GhostState.CHASE
                    # Check for Game Over condition
                    if self.player.lives <= 0:
                        self.is_game_over = True
                    return

    def _check_win_condition(self) -> None:
        """
        Checks if all pacgums (2) and super-pacgums (3) have been eaten.
        If yes, advances to next level
        """
        # We scan the grid to see if any items are left
        for row in self.maze.items:
            if 2 in row:
                return
        print(f"Level {self.current_level} Complete!")
        self.current_level += 1
        if self.current_level > 10:
            self.current_level = 10
            self.is_victory = True
            print("You won the game!")
        else:
            # generate a new random maze
            self.load_level()

    def _get_valid_directions(self, x: int, y: int,
                              current_direction: str = "") -> list:
        """
        Returns a list of valid directions.
        """
        valid_dirs = []
        # We test all 4 possible directions
        for d in [Direction.UP, Direction.DOWN, Direction.LEFT,
                  Direction.RIGHT]:
            if self.maze.can_move(x, y, d.name):
                valid_dirs.append(d)
            if len(valid_dirs) > 1 and current_direction:
                opposite = None
                if current_direction == "UP":
                    opposite = Direction.DOWN
                elif current_direction == "DOWN":
                    opposite = Direction.UP
                elif current_direction == "LEFT":
                    opposite = Direction.RIGHT
                elif current_direction == "RIGHT":
                    opposite = Direction.LEFT
                if opposite in valid_dirs:
                    valid_dirs.remove(opposite)
        return valid_dirs

    def _find_shortest_path(self, start_x: int, start_y: int,
                            target_x: int, target_y: int
                            ) -> None | tuple[int, int, None]:
        """
        Find the shortest path using BFS
        """
        # (x, y, 1ère_direction_prise)
        queue = [(start_x, start_y, None)]
        visited = {(start_x, start_y)}
        for cx, cy, first_dir in queue:
            if cx == target_x and cy == target_y:
                return first_dir
            for d in [Direction.UP, Direction.DOWN,
                      Direction.LEFT, Direction.RIGHT]:
                if self.maze.can_move(cx, cy, d.name):
                    nx, ny = cx + d.value[0], cy + d.value[1]
                    if (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append((nx, ny, first_dir if first_dir else d))
        return None

    def _move_ghosts(self) -> None:
        """
        Handles the autonomous movement of all ghosts based on their state.
        """
        for ghost in self.ghosts:
            if ghost.state == GhostState.EDIBLE:
                ghost.speed = 0.03
            else:
                ghost.speed = 0.05
            if ghost.state == GhostState.DEAD:
                continue
            if ghost.destx == -1:
                # get instant coordinates of pacman
                px = self.player.x
                py = self.player.y
                # Find all directions the ghost can legally move to
                valid_dirs = self._get_valid_directions(
                    ghost.x,
                    ghost.y,
                    ghost.direction)
                if not valid_dirs:
                    continue  # security check , should never be used
                if ghost.state == GhostState.EDIBLE:
                    best_dir = max(valid_dirs,
                                   key=lambda
                                   m: abs((ghost.x + m.value[0]) - px)
                                   + abs((ghost.y + m.value[1]) - py))
                    dx, dy = best_dir.value
                else:
                    # distance between pacman & ghost
                    distance = abs(ghost.x - px) + abs(ghost.y - py)
                    sniper = 10
                    if distance <= sniper:
                        best_dir = self._find_shortest_path(ghost.x, ghost.y,
                                                            px, py)
                        if best_dir is None or best_dir not in valid_dirs:
                            best_dir = random.choice(valid_dirs)
                    # Pick a random valid direction!
                    else:
                        best_dir = random.choice(valid_dirs)
                    dx, dy = best_dir.value
                destx = ghost.x + dx
                desty = ghost.y + dy
                if destx < ghost.x:
                    ghost.direction = "LEFT"
                elif destx > ghost.x:
                    ghost.direction = "RIGHT"
                elif desty < ghost.y:
                    ghost.direction = "UP"
                else:
                    ghost.direction = "DOWN"
                ghost.destx = destx + 0.5
                ghost.desty = desty + 0.5
            rail_movements(ghost)

    def reset_game(self) -> None:
        """
        Hard reset of the engine to start a brand new game from the Main Menu.
        """
        self.score = 0
        self.current_level = 1
        self.is_game_over = False
        self.is_victory = False
        self.player_died_event = False
        self.load_level()

    def update(self, delta_time: float) -> None:
        """
        The main game loop logic. to update the game state.
        """
        if self.is_game_over or self.is_victory:
            return
        self.time_left -= delta_time
        if self.time_left <= 0:
            if self.cheat_invincible:
                self.time_left = 1
            else:
                self.is_game_over = True
                print("Time's up! Game Over.")
            return
        # Update ghost timers
        for ghost in self.ghosts:
            ghost.update_timer(delta_time)
        # Move Player
        self._move_player()
        rail_movements(self.player)
        # Move Ghosts
        self._move_ghosts()
        # Player eating pacgums or touching ghosts
        self._check_collisions()
        # Check Level Completion
        self._check_win_condition()

    def get_state(self) -> dict:
        """
        Convert game stat to a dict
        """
        return {
            "hud": {
                "score": self.score,
                "lives": self.player.lives,
                "level": self.current_level,
                "time_left": int(self.time_left),
                "is_game_over": self.is_game_over,
                "is_victory": self.is_victory
            },
            "maze": self.maze.grid,  # une liste de listes
            "player": {
                "x": self.player.x,
                "y": self.player.y,
                "direction": self.player.current_direction.name
            },
            "ghosts": [
                {
                    "color_id": g.color_id,
                    "x": g.x,
                    "y": g.y,
                    "state": g.state.name
                } for g in self.ghosts
            ]
        }
