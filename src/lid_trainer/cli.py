"""Entry point for lid-trainer — launches the web UI."""

import argparse

from lid_trainer.questions import STATES, QuestionBank
from lid_trainer.web import run_web


def main() -> None:
    """Launch the web UI."""
    parser = argparse.ArgumentParser(description="Leben in Deutschland Trainer — Web UI")
    parser.add_argument(
        "--state",
        choices=STATES,
        default="Berlin",
        help="Your Bundesland (default: Berlin)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5050,
        help="Port for the web server (default: 5050)",
    )
    args = parser.parse_args()

    bank = QuestionBank()
    run_web(bank, args.state, args.port)


if __name__ == "__main__":
    main()
