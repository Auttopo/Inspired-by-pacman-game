import json
import sys
from typing import Any, Dict


class GameConfig:
    """
    Manange charging and validation of config game
    """
    def __init__(self, filepath: str) -> None:
        """
        Initialise config with path file and default values.
        """
        self.filepath = filepath
        self.settings: Dict[str, Any] = {
            "highscore_filename": "highscores.json",
            "lives": 3,
            "points_per_pacgum": 10,
            "points_per_super_pacgum": 50,
            "points_per_ghost": 200,
            "seed": 42,
            "level": [
                {"width": 15, "height": 15},  # Niveau 1
                {"width": 25, "height": 25},  # Niveau 2
                {"width": 31, "height": 31},   # Niveau 3
                {"width": 80, "height": 21},  # Niveau 4
                {"width": 45, "height": 23},  # Niveau 5
                {"width": 31, "height": 31},   # Niveau 6
                {"width": 50, "height": 55},  # Niveau 7
                {"width": 31, "height": 80},   # Niveau 8
                {"width": 80, "height": 80},   # Niveau 9
                {"width": 10, "height": 10},   # Niveau 10
            ]
        }
        self.load_config()

    def _remove_comments(self, json_string: str) -> str:
        """
       delete lines starting with '#'
        """
        lines = json_string.split('\n')
        cleaned_lines = [line for line in lines
                         if not line.strip().startswith('#')]
        return '\n'.join(cleaned_lines)

    def load_config(self) -> None:
        """
        Charge JSON file, ignore comments & update params.
        handle errors properly
        """
        try:
            with open(self.filepath, 'r', encoding='utf-8') as file:
                raw_content = file.read()
            clean_content = self._remove_comments(raw_content)
            user_settings = json.loads(clean_content)
            for key, value in user_settings.items():
                if key not in self.settings.keys():
                    print(
                        f"[WARNING] unknow key skipped : {key}",
                        file=sys.stderr)
                    continue
                if key in self.settings:
                    self.settings[key] = value
            defaults_points = {
                'points_per_pacgum': 10,
                'points_per_super_pacgum': 50,
                'points_per_ghost': 200
            }
            for key, default_val in defaults_points.items():
                try:
                    val = int(self.settings[key])
                    self.settings[key] = max(1, min(val, 100000))
                except (ValueError, TypeError):
                    self.settings[key] = default_val
                    print(f"[WARNING] '{key}' is invalid. "
                          f"Defaulting to {default_val}.", file=sys.stderr)

            try:
                lives = int(self.settings['lives'])
                self.settings['lives'] = max(1, min(lives, 99))
            except (ValueError, TypeError):
                self.settings['lives'] = 3
                print("[WARNING] 'lives' must be a valid number. "
                      "Defaulting to 3.", file=sys.stderr)

            levels = self.settings.get('level')
            if not isinstance(levels, list) or len(levels) == 0:
                print("[WARNING] 'level' is missing or empty. "
                      "Using default level 1.", file=sys.stderr)
                # we give at least level 1
                self.settings['level'] = [{"width": 15, "height": 15}]
            else:
                valid_levels = []
                for i, lvl in enumerate(levels):
                    if not isinstance(lvl, dict):
                        continue

                    #  Width security
                    try:
                        w = int(lvl.get('width', 25))
                        w = max(10, min(w, 65))
                    except (ValueError, TypeError):
                        print(f"[WARNING] Level {i} width is invalid. "
                              f"Defaulting to 25.", file=sys.stderr)
                        w = 25

                    # Height security
                    try:
                        h = int(lvl.get('height', 25))
                        h = max(10, min(h, 65))
                    except (ValueError, TypeError):
                        print(f"[WARNING] Level {i} height is invalid. "
                              f"Defaulting to 25.", file=sys.stderr)
                        h = 25

                    valid_levels.append({"width": w, "height": h})

                if len(valid_levels) == 0:
                    print("[WARNING] No valid levels parsed. "
                          "Using default level 1.", file=sys.stderr)
                    valid_levels = [{"width": 15, "height": 15}]

                self.settings['level'] = valid_levels

                if not isinstance(self.settings['seed'], int):
                    self.settings['seed'] = 42
                if self.settings['seed'] < 1:
                    self.settings['seed'] = 42

                if not isinstance(self.settings["highscore_filename"], str):
                    self.settings["highscore_filename"] = "highscores.json"

            for key, elem in self.settings.items():
                if user_settings.get(key) is None:
                    print(
                        f"[WARNING] missing key '{key}' set to: {elem}",
                        file=sys.stderr)
                elif key == "level" and \
                        isinstance(user_settings["level"], list):
                    for i, one_lvl in enumerate(
                                                self.settings["level"],
                                                start=1):
                        if one_lvl not in user_settings["level"]:
                            print(
                                f"[WARNING] wrong level ({i})"
                                f" set to: {one_lvl}",
                                file=sys.stderr)
                    if len(user_settings["level"]) > 10:
                        print(
                            "[WARNING] too much levels, only 10 first used",
                            file=sys.stderr)
                    if len(user_settings["level"]) < 10:
                        print(
                            "[WARNING] not enought levels, "
                            "last level knowed arguments used till level 10",
                            file=sys.stderr)
                elif elem != user_settings[key]:
                    print(
                        f"[WARNING] from '{key}' wrong value "
                        f"'{user_settings[key]}' set to: {elem}",
                        file=sys.stderr)

        except FileNotFoundError:
            print(f"[WARNING] The file '{self.filepath}' could not be found. "
                  f"Using default settings: {self.settings}", file=sys.stderr)
        except json.JSONDecodeError as e:
            print(f"[WARNING] The file '{self.filepath}' contains invalid JSON"
                  f" ({e}). Using default settings: {self.settings}",
                  file=sys.stderr)
        except Exception as e:
            print(f"{e}[WARNING] Unexpected error while reading the config."
                  f" Using default settings: {self.settings}", file=sys.stderr)

        print(f"Configuration successfully loaded from {self.filepath}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Error. Usage : python3 pac-man.py config.json")
    else:
        config = GameConfig(sys.argv[1])
        print("Parameters ready for the game: ", config.settings)
