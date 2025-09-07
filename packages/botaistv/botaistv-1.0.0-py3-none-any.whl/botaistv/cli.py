import sys
from .core import run_ai_helper, stop_ai_helper

def main():
    if len(sys.argv) < 2:
        print(" Dùng: stv [on|off]")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "on":
        run_ai_helper()
    elif cmd == "off":
        stop_ai_helper()
    else:
        print("Lệnh không hợp lệ. Dùng: stv [on|off]")