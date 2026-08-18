
from inputs.input_process import InputProcesses
from inputs.input_sdl_engine import SDLCoreEngine
from typing import Callable, Iterator
import threading

GAME_SERVER_MUTEX = threading.Lock()

class InputEngine(InputProcesses, SDLCoreEngine):
    """
    The master engine for handling the game loop and user inputs."""

    def create_frames_generator(self) -> Callable[..., Iterator[bytes]]:

        def generate_http_frames():
            GAME_SERVER_MUTEX.acquire()
            gen = self.process_core_while()
            try:
                while 1:
                    yi = next(gen)
                    yield(
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n\r\n"
                        + yi + b"\r\n")
            except Exception:
                raise
            finally:
                self.free_all()
                GAME_SERVER_MUTEX.release()

        return generate_http_frames
