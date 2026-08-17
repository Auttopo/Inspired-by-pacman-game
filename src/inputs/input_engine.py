
from inputs.input_process import InputProcesses
from inputs.input_sdl_engine import SDLCoreEngine


class InputEngine(InputProcesses, SDLCoreEngine):
    """
    The master engine for handling the game loop and user inputs."""

    def process_game(self) -> None:
        """
        Starts and manages the main game loop.
        Attempts to run the core 'while' loop of the game. If an exception
        occurs during gameplay, it catches it and re-raises it to be handled
        (or logged) by the caller. """
        try:
            self.process_core_while()
        except Exception:
            raise
        finally:
            self.free_all()
