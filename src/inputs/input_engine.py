
from inputs.input_process import InputProcesses
from inputs.input_sdl_engine import SDLCoreEngine
from typing import Callable, Iterator


class InputEngine(InputProcesses, SDLCoreEngine):
    """
    The master engine for handling the game loop and user inputs."""

    def create_frames_generator(self) -> Callable[..., Iterator[bytes]]:
        gen = self.process_core_while()

        def generate_http_frames():
            try:
                while 1:
                    yi = next(gen)
                    yield(
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n\r\n"
                        + yi + b"\r\n")
            except Exception as e:
                print(f"Unexpected error ! : {e}")
            finally:
                self.stream_mutex.release()

        return generate_http_frames
