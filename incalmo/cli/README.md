# Incalmo CLI

A simple CLI REPL tool frontend for Incalmo.

## Installation

Using uv (recommended):

```bash
uv pip install -e .
```

Or with pip:

```bash
pip install -e .
```

## Usage

Start the interactive REPL:

```bash
incalmo-cli
```

Or using Python module:

```bash
uv run python -m incalmo_cli
```

## Commands

- `hello [name]` - Say hello
- `echo <message>` - Echo input
- `status` - Show session status
- `set <key> <value>` - Set session variable
- `get <key>` - Get session variable
- `clear` - Clear session data
- `exit`/`quit` - Exit REPL