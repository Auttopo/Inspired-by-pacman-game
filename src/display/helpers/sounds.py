
import sdl2.sdlmixer as s2_mix
from pathlib import Path
from typing import Any

SOUNDS_PATH = [
        "assets/",
        "eat_sound1.wav",
        "eat_sound2.wav",
        "eat_sound3.wav",
        "death_sound.wav",
        "win_sound.wav",
        "left_life_sound.wav",
        "menu_sound.wav",
        "game_sound.wav",
]


class SoundsError(Exception):
    """Custom exception raised when a sound fails to load"""
    pass


class Sounds:
    """
    Manages game audio, including sound effects and background music
    """
    def __init__(self) -> None:
        self.sounds: dict[str, Any] = dict()
        self.is_active = False
        self.active: str = ""
        self.music_off = False

    def load_sounds(self) -> None:
        """
        Loads all WAV files specified in SOUNDS_PATH into memory.
        The sounds are stored in the self.sounds """
        for elem in SOUNDS_PATH[1:]:
            path = f"{SOUNDS_PATH[0]}{elem}"
            chunk = s2_mix.Mix_LoadWAV(path.encode())
            if not chunk:
                raise SoundsError(f"Can't load sound : {path}")
            name = Path(elem).name.removesuffix(".wav")
            self.sounds.update({name: chunk})
        return

    def free_all_sounds(self) -> None:
        """
        Frees the memory allocated for all loaded sound chunks and
        properly shuts down the SDL2 mixer audio subsystem.
        """
        for key, elem in self.sounds.items():
            s2_mix.Mix_FreeChunk(elem)
        s2_mix.Mix_CloseAudio()
        s2_mix.Mix_Quit()

    def set_background_sound(self, name: str, loop: int = -1) -> None:
        """
        Plays or resumes a specific background sound/music"""
        if not self.is_active:
            self.channel = s2_mix.Mix_PlayChannel(-1, self.sounds[name], loop)
            self.active = name
            self.is_active = True
        elif name == self.active:
            s2_mix.Mix_Resume(self.channel)
        else:
            s2_mix.Mix_HaltChannel(self.channel)
            self.channel = s2_mix.Mix_PlayChannel(-1, self.sounds[name], loop)
            self.active = name
        if self.music_off:
            self.halt_background_sound()

    def halt_background_sound(self) -> None:
        """
        Pauses the currently playing background sound channel
        The sound can be resumed later
        """
        if self.active:
            s2_mix.Mix_Pause(self.channel)

    def music_off_background_sound(self, mode: bool) -> None:
        """
        Toggles the global background music state (muted or unmuted)."""
        self.music_off = mode
        if self.is_active:
            if mode:
                self.halt_background_sound()
            else:
                s2_mix.Mix_Resume(self.channel)
