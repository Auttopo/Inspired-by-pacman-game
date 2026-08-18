
import sys
from inputs.input_engine import InputEngine
from flask import Flask, Response
from flask_sock import Sock
server_app = Flask(__name__)
route_app = Sock(server_app)


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
        game = InputEngine(sys.argv[1])
        game.init_game()
        frame_gen = game.create_frames_generator()

        @server_app.route("/stream")
        def stream_game():
            return Response(
                        frame_gen(),
                        mimetype="multipart/x-mixed-replace; boundary=frame")

        @route_app.route("/inputs")
        def stream_inputs(websocket):
            while True:
                data = websocket.receive()
                if data is None:
                    break
                print(data)

        server_app.run(host=host, port=port, threaded=True)

    except KeyboardInterrupt:
        print("program killed from keyboard", file=sys.stderr)
    except Exception as e:
        print(f"fatal error: {e}", file=sys.stderr)
