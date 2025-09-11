#!/usr/bin/env python3

import argparse
import sys
from incalmo.cli.repl import main as repl_main


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="incalmo-cli", description="Incalmo CLI Tool with Textual TUI"
    )

    parser.add_argument("--version", action="version", version="Incalmo CLI 0.1.0")

    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Start interactive REPL mode (default)",
    )

    args = parser.parse_args()

    # Default to interactive mode
    if args.interactive or len(sys.argv) == 1:
        repl_main()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
