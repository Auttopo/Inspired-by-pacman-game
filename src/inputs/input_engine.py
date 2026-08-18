
from inputs.input_process import InputProcesses
from inputs.input_sdl_engine import SDLCoreEngine
from typing import Callable, Iterator
import threading
from flask import Response

STREAM_MUTEX = threading.Lock()

class InputEngine(InputProcesses, SDLCoreEngine):
    """
    The master engine for handling the game loop and user inputs."""

    def create_frames_generator(self) -> Callable[..., Iterator[bytes]]:
        gen = self.process_core_while()

        def generate_http_frames():
            global STREAM_MUTEX
            if not STREAM_MUTEX.acquire(blocking=False):
                return Response("Stream already in use", status=409, mimetype="text/plain")
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
                STREAM_MUTEX.release()

        return generate_http_frames
