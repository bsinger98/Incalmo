#!/usr/bin/env python3
"""
Entry point for Incalmo CLI REPL - now using modular architecture
"""

import sys
from incalmo.cli.app import IncalmoREPL


def main():
    """Main entry point for the CLI REPL"""
    import signal

    def signal_handler(sig, frame):
        print("\nGoodbye!")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        app = IncalmoREPL()
        app.run()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
