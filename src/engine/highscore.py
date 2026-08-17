import json
import os
import sys
from typing import List, Dict, Any


class HighscoreManager:
    """Reading high scores"""
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.scores: List[Dict[str, Any]] = []
        self.load_scores()

    def load_scores(self) -> None:
        """Charging scores from json file"""
        if not os.path.exists(self.filepath):
            self.scores = []
            return
        try:
            with open(self.filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if isinstance(data, list):
                    valid_scores = []
                    for entry in data:
                        if (isinstance(entry, dict) and
                                isinstance(entry.get("name"), str)
                                and str(entry.get("name")).isalnum()
                                and isinstance(entry.get("score"), int)):
                            data_score: int = int(str(entry.get("score")))
                            if data_score >= 0:
                                valid_scores.append(entry)
                    self.scores = valid_scores
                else:
                    self.scores = []
        except (json.JSONDecodeError, IOError):
            print(
                "[WARNING] Can't read highscores file or corrupted format.",
                file=sys.stderr)
            self.scores = []

    def save_scores(self) -> None:
        """Save list of actual scores"""
        try:
            # w to creat file id doesn't exist
            with open(self.filepath, 'w', encoding='utf-8') as file:
                json.dump(self.scores, file, indent=4)
        except IOError as e:
            print(f"[ERROR] Error while saving scores : {e}", file=sys.stderr)

    def clean_player_name(self, name: str) -> str:
        """Clean and return valid name"""
        if not name:
            return "UNKNOWN"
        clean_name = ''.join(c for c in name if c.isalnum() or c.isspace())
        return clean_name[:10] if clean_name else "UNKNOWN"

    def add_score(self, player_name: str, score: int) -> None:
        """add score and save just Top 10"""
        if not isinstance(score, int):
            return
        if score < 0:
            score = 0
        player_name = self.clean_player_name(player_name)
        # add to list
        self.scores.append({"name": player_name, "score": score})
        # sorting list
        self.scores.sort(key=lambda x: x["score"], reverse=True)
        # save just 10
        self.scores = self.scores[:10]
        self.save_scores()
