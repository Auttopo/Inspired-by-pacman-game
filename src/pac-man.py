
import sys
import threading
from inputs.input_engine import InputEngine
import sdl2 as s2
import json
from flask import Flask, Response
from flask_sock import Sock
server_app = Flask(__name__)
route_app = Sock(server_app)


def event_mapping(inputs: dict[str, str]):

    print(inputs)
    match inputs["type"]:
        case "mouseup":
            event = s2.SDL_Event()
            event.type = s2.SDL_MOUSEBUTTONUP
            print("MOUSE")
            if inputs["button"] == 0:
                event.button.button = s2.SDL_BUTTON_LEFT
                event.button.x = inputs["x"]
                event.button.y = inputs["y"]
                s2.SDL_PushEvent(event)
                print("UPSHED")

        case "keydown":
            event = s2.SDL_Event()
            event.type = s2.SDL_KEYDOWN
            match inputs["key"]:
                case "w" | "ArrowUp":
                    event.key.keysym.sym = s2.SDLK_UP
                    s2.SDL_PushEvent(event)
                case "d" | "ArrowRight":
                    event.key.keysym.sym = s2.SDLK_RIGHT
                    s2.SDL_PushEvent(event)
                case "s" | "ArrowDown":
                    event.key.keysym.sym = s2.SDLK_DOWN
                    s2.SDL_PushEvent(event)
                case "a" | "ArrowLeft":
                    event.key.keysym.sym = s2.SDLK_LEFT
                    s2.SDL_PushEvent(event)
                case "Escape":
                    event.key.keysym.sym = s2.SDLK_ESCAPE
                    s2.SDL_PushEvent(event)
                case "/":
                    event.key.keysym.sym = s2.SDLK_SLASH
                    s2.SDL_PushEvent(event)
                case "Enter":
                    event.key.keysym.sym = s2.SDLK_RETURN
                    s2.SDL_PushEvent(event)

            event2 = s2.SDL_Event()
            event2.type = s2.SDL_TEXTINPUT
            event2.text.text = inputs["key"].encode("utf-8")
            s2.SDL_PushEvent(event2)

        case "resize":
            event = s2.SDL_Event()
            event.type = s2.SDL_WINDOWEVENT
            event.window.event = s2.SDL_WINDOWEVENT_RESIZED
            event.window.data1 = inputs["width"]
            event.window.data2 = inputs["height"]
            s2.SDL_PushEvent(event)


if __name__ == "__main__":
    port = 8042
    host = "0.0.0.0"
    if len(sys.argv) < 2 or len(sys.argv) > 4:
        print(
            "Error. Usage : python3 pac-man.py "
            "config.json optional:port optional:host",
            file=sys.stderr)
        sys.exit(1)
    if len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except:
            print("Error : port need to be integer", file=sys.stderr)
            sys.exit(1)
    if len(sys.argv) > 3:
        host = sys.argv[3]

    try:
        mutex = threading.Lock()

        @server_app.route("/stream")
        def stream_game():
            game = InputEngine(sys.argv[1])
            game.init_game()
            game.mutex = mutex
            frame_gen = game.create_frames_generator()
            return Response(
                        frame_gen(),
                        mimetype="multipart/x-mixed-replace; boundary=frame")

        @route_app.route("/inputs")
        def stream_inputs(websocket):
            while True:
                data = websocket.receive()
                if data is None:
                    break
                mutex.acquire()
                event_mapping(json.loads(data))
                mutex.release()

        server_app.run(host=host, port=port, threaded=True)

    except KeyboardInterrupt:
        print("program killed from keyboard", file=sys.stderr)
    except Exception as e:
        print(f"fatal error: {e}", file=sys.stderr)
