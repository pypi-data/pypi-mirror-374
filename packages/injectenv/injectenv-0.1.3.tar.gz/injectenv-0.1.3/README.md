# injectenv

A simple and flexible command-line tool for injecting environment variables into spawned processes.

## Features

- **Multiple sources**: Load variables from command-line flags, `.env` files, and profiles
- **Flexible precedence**: Customize which sources override others with `--order`
- **Profile support**: Load environment-specific configs with `.env.<profile>` files
- **JSON output**: Export merged environment as JSON for debugging or integration
- **Shell support**: Run commands through shell or directly
- **Dry-run mode**: Preview environment variables without executing commands

## Installation

```bash
pip install injectenv
```

## Quick Start

````bash
# Set variables and run a command
# injectenv

A small command-line tool to merge environment variables from files and flags and inject them into a spawned process.

## Key points (what the code actually does)

- Loads variables from explicit `-f/--file` files and from `-e/--env` flags.
- Does NOT auto-load `./.env` and there is no profile support (the `--profile` option is not implemented).
- When any `-f` or `-e` is provided, the current system environment is excluded by default. If neither `-f` nor `-e` are given, the tool will include the current process environment.
- Precedence is configurable via `--order` but the CLI enforces that `--order` is a comma list containing exactly: `system,file,flags` (each token once). Rightmost token wins.
- `--override` is a legacy flag kept for parity but has no special behavior beyond the default ordering unless you change `--order` explicitly.

## Installation

```bash
pip install injectenv
````

or, if you like to have the cli installed gloabally:

```bash
pipx install injectenv
```

## Usage

```
injectenv [OPTIONS] [--] COMMAND [ARGS...]
```

Options you'll actually find:

- `-e, --env KEY=VAL` : Set an env var (repeatable). Example: `-e FOO=bar -e X=1`.
- `-f, --file FILE` : Load vars from a .env-like file (repeatable). Files must be provided explicitly; missing files are an error.
- `--order ORDER` : Comma-separated tokens from low→high priority (rightmost wins). Valid tokens are `system,file,flags` and the argument must include each exactly once (default: `system,file,flags`).
- `-o, --override` : Legacy boolean flag. Kept for backwards compatibility; ignored if you pass a custom `--order` that differs from the default.
- `--unset KEY` : Remove variable(s) from the final env before spawning (repeatable).
- `--print-env` : Print merged environment as `KEY=VAL` lines before running the command.
- `--json` : Print merged environment as JSON and exit (does not run the command).
- `-s, --shell` : Run the command through a shell (be careful with quoting).
- `--no-inherit-stdio`: Do not inherit stdio; stream output instead (useful for capturing output programmatically).

Notes about behavior:

- `-f` does not auto-load `./.env`. You must pass files explicitly.
- If you pass any `-f` or any `-e`, the current system environment is NOT included unless you explicitly include `system` in `--order` (the default order includes it only when neither `-f` nor `-e` are passed).
- File loading: the loader uses `python-dotenv` to parse files; for a given `file` source, later files override earlier files (last one wins inside the `file` layer).
- `--order` is strictly validated: it must contain the three tokens `system,file,flags` exactly once each.

## Examples

Basic variable injection with flags:

```bash
injectenv -e API_KEY=secret123 -- curl -H "Authorization: $API_KEY" https://api.example.com
```

Load variables from a file and override with flags:

```bash
injectenv -f .env -e DEBUG=true -- python app.py
```

Print the merged env as JSON and exit:

```bash
injectenv -f .env --json
```

Print KEY=VAL lines and exit (no command):

```bash
injectenv -f .env --print-env
```

Unset a sensitive variable before running:

```bash
injectenv -f .env --unset SECRET_KEY -- python app.py
```

Custom precedence (rightmost wins):

```bash
# Make flags have the lowest precedence and files win over system vars
injectenv --order flags,system,file -f .env -e NODE_ENV=development -- node app.js
```

## File format

Standard `.env` format is supported (parsed with `python-dotenv`):

```env
# .env
NODE_ENV=development
PORT=3000
DEBUG=true
```

## Requirements

- Python 3.9+
- python-dotenv

## License

MIT License - see LICENSE file for details.
