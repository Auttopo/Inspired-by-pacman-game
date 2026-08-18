
import sys
from inputs.input_engine import InputEngine
from flask import Flask, Response
server_app = Flask(__name__)



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Error. Usage : python3 pac-man.py config.json")
        sys.exit(1)
    try:
        game = InputEngine(sys.argv[1])
        game.init_game()
        frame_gen = game.create_frames_generator()

        @server_app.route("/stream")
        def stream_game():
            return Response(
                        frame_gen(),
                        mimetype="multipart/x-mixed-replace; boundary=frame")
        server_app.run(host="0.0.0.0", port=8000, threaded=True)

    except KeyboardInterrupt:
        print("program killed from keyboard", file=sys.stderr)
    except Exception as e:
        print(f"fatal error: {e}", file=sys.stderr)
