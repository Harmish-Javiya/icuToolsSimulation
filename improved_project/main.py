import argparse

from ui import run_app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the defibrillator simulator UI and API")
    parser.add_argument("--port", type=int, default=8000, help="Port for the simulator HTTP API")
    args = parser.parse_args()
    run_app(port=args.port)
