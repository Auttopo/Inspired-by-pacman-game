
import sys
from inputs.input_engine import InputEngine

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Error. Usage : python3 pac-man.py config.json")
        sys.exit(1)
    try:
        game = InputEngine(sys.argv[1])
        game.init_game()
        game.process_game()
    except KeyboardInterrupt:
        print("program killed from keyboard", file=sys.stderr)
    except Exception as e:
        print(f"fatal error: {e}", file=sys.stderr)
