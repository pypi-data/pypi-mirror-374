#!/usr/bin/env python3
"""
injectenv.py - A simple CLI tool to inject environment variables into a spawned
process or to print them out.  This is a refactored implementation of a small
utility that allows environment variables to come from three sources: the
current system environment, one or more .env files, and explicit key=value
pairs passed on the command line.  The precedence order is fixed: values
provided via the ``-e/--env`` flag override values loaded from ``-f/--file``
files, which in turn override the current system environment.  When any file
or flag is provided, the system environment is ignored unless ``--with-system``
is explicitly requested.  When neither ``-f`` nor ``-e`` is used, the tool
defaults to using the current system environment.

Usage examples::

    # Run ``myapp`` inheriting the entire system environment
    injectenv -- myapp

    # Inject variables from a file without inheriting the system environment
    injectenv -f .env -- myapp

    # Inject variables from a file *and* from the system environment
    injectenv -f .env --with-system -- myapp

    # Override a variable from the file on the command line
    injectenv -f .env -e FOO=bar -- myapp

    # Print the resulting environment as JSON without running a command
    injectenv -f .env --json

This script intentionally avoids depending on ``python-dotenv`` for parsing
.env files to keep dependencies minimal.  It implements a very simple .env
parser that understands ``key=value`` pairs separated by the first ``=`` in
each non-empty, non-comment line.
"""

import argparse
import json
import os
import subprocess
import sys
from typing import Dict, List


def build_parser() -> argparse.ArgumentParser:
    """Construct the command‑line argument parser.

    Supported options:

    - ``-e/--env KEY=VAL``: specify environment variables explicitly.  May be
      provided multiple times.  Later occurrences overwrite earlier ones.
    - ``-f/--file PATH``: load variables from a .env-like file.  May be
      provided multiple times.  When multiple files are supplied, variables
      loaded from later files override those from earlier files.
    - ``--with-system``: when any ``-f`` or ``-e`` flag is used, include the
      current system environment when merging.  Without this flag, system
      variables are ignored when custom sources are used.
    - ``--unset KEY``: remove a variable from the merged environment before
      spawning.  May be provided multiple times.
    - ``--print-env``: print the merged environment as ``KEY=VAL`` lines
      immediately before running the command.
    - ``--json``: print the merged environment as a JSON object and exit
      without running a command.
    - ``-s/--shell``: execute the command via the shell.  Be careful with
      quoting when using this mode.
    - ``--no-inherit-stdio``: do not inherit standard IO of the current
      process.  Instead, capture and stream the child’s output.
    - ``--``: separate the tool’s flags from the command and its arguments.

    Positional arguments following ``--`` are treated as the command to run.
    If no command is provided, the tool will print the environment (if
    requested) and exit.
    """
    parser = argparse.ArgumentParser(
        prog="injectenv", description="Inject environment variables into a spawned process."
    )
    # Environment variable sources
    parser.add_argument(
        "-e",
        "--env",
        action="append",
        default=[],
        metavar="KEY=VAL",
        help="Set an environment variable (repeatable). Example: -e FOO=bar -e X=1",
    )
    parser.add_argument(
        "-f",
        "--file",
        action="append",
        default=[],
        help="Load variables from a .env-like file (repeatable).",
    )
    parser.add_argument(
        "--with-system",
        action="store_true",
        help=(
            "When using -f or -e, also include variables from the current system environment."
        ),
    )
    # Behaviour / merging semantics
    parser.add_argument(
        "--unset",
        action="append",
        default=[],
        metavar="KEY",
        help="Unset/remove variable(s) before spawning (repeatable)",
    )
    # Output / dry-run modes
    parser.add_argument(
        "--print-env",
        action="store_true",
        help="Print merged environment as KEY=VAL lines before running",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print merged environment as JSON and exit (does NOT run the command)",
    )
    # Process execution flags
    parser.add_argument(
        "-s",
        "--shell",
        action="store_true",
        help="Run the command through the shell (be careful with quoting)",
    )
    parser.add_argument(
        "--no-inherit-stdio",
        action="store_true",
        help="Do not inherit stdio; stream output instead",
    )
    # The '--' sentinel allows disambiguating commands that begin with a dash.
    parser.add_argument(
        "--",
        dest="double_dash",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Command to run (prefix with -- to disambiguate)",
    )
    return parser


def parse_pairs(pairs: List[str]) -> Dict[str, str]:
    """Parse a sequence of KEY=VAL strings into a dictionary.

    Raises ``SystemExit`` if any element does not contain an ``=`` or if the
    key part is empty.
    """
    result: Dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise SystemExit(f"Invalid --env value (expected KEY=VAL): {pair}")
        key, value = pair.split("=", 1)
        key = key.strip()
        if not key:
            raise SystemExit(f"Invalid key in: {pair}")
        result[key] = value
    return result


def load_files(files: List[str]) -> Dict[str, str]:
    """Load environment variables from the given list of files.

    Only files explicitly provided are read.  Each file is parsed in order,
    and variables from later files override those from earlier files.  A very
    simple .env parser is used: lines beginning with ``#`` or blank lines are
    ignored, and the first ``=`` separates the key from the value.

    Raises ``SystemExit`` if any specified file does not exist.
    """
    env: Dict[str, str] = {}
    for path in files:
        if not os.path.exists(path):
            raise SystemExit(f"--file not found: {path}")
        try:
            with open(path, "r", encoding="utf-8") as fh:
                for line in fh:
                    stripped = line.strip()
                    # Skip comments and empty lines
                    if not stripped or stripped.startswith("#"):
                        continue
                    if "=" not in stripped:
                        # Ignore malformed lines
                        continue
                    k, v = stripped.split("=", 1)
                    k = k.strip()
                    v = v.strip()
                    env[k] = v
        except OSError as exc:
            raise SystemExit(f"Error reading --file {path}: {exc}")
    return env


def merge_env(system: Dict[str, str], filemap: Dict[str, str], flags: Dict[str, str]) -> Dict[str, str]:
    """Merge the three environment maps according to fixed precedence.

    Values from ``flags`` override those from ``filemap``, which in turn
    override those from ``system``.  None of the input dictionaries are
    modified; a new dictionary is returned.
    """
    merged: Dict[str, str] = {}
    # Lowest precedence: system
    merged.update(system)
    # Medium precedence: file
    merged.update(filemap)
    # Highest precedence: command line flags
    merged.update(flags)
    return merged


def apply_unset(envmap: Dict[str, str], keys: List[str]) -> Dict[str, str]:
    """Remove specified keys from the environment mapping.

    Returns a new dictionary with the specified keys removed.  If a key is
    listed multiple times, subsequent occurrences have no further effect.
    """
    if not keys:
        return dict(envmap)
    env = dict(envmap)
    for key in keys:
        env.pop(key, None)
    return env


def stream_process(proc: subprocess.Popen) -> None:
    """Stream the child process's stdout and stderr to the current process.

    When ``--no-inherit-stdio`` is used, the child is launched with its
    stdout/stderr pipes captured.  This helper reads from those pipes and
    writes the data to the corresponding streams on the parent process.  It
    stops when the child process closes its streams.  KeyboardInterrupt is
    ignored so that the caller can decide how to handle interrupts.
    """
    try:
        if proc.stdout is not None:
            for line in iter(proc.stdout.readline, b""):
                sys.stdout.buffer.write(line)
                sys.stdout.buffer.flush()
        if proc.stderr is not None:
            for line in iter(proc.stderr.readline, b""):
                sys.stderr.buffer.write(line)
                sys.stderr.buffer.flush()
    except KeyboardInterrupt:
        # Allow caller to handle Ctrl+C
        pass


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Handle command after "--" sentinel.  argparse includes the "--" in
    # args.command if it was used to separate options from the command; drop
    # it to avoid confusing subprocess.
    cmd = args.command
    if cmd and cmd[0] == "--":
        cmd = cmd[1:]

    # Parse environment variables from flags and files
    flags_map = parse_pairs(args.env)
    files_map = load_files(args.file)

    # Determine whether to include system environment
    include_system = False
    if not args.file and not args.env:
        # No custom sources → always include system env
        include_system = True
    elif args.with_system:
        # User explicitly requested system env along with custom sources
        include_system = True

    system_source: Dict[str, str] = os.environ if include_system else {}

    # Merge sources according to fixed precedence (system < file < flags)
    merged = merge_env(system_source, files_map, flags_map)
    merged = apply_unset(merged, args.unset)

    # Output modes
    if args.json:
        # JSON always prints and exits without running a command
        print(json.dumps(merged, ensure_ascii=False, indent=2))
        raise SystemExit(0)

    if args.print_env:
        for key, value in merged.items():
            # Print each environment assignment immediately and flush to avoid
            # interleaving with the child process's output when piping
            print(f"{key}={value}", flush=True)

    # If no command is provided, exit after printing (if requested)
    if not cmd:
        # If user requested printing only, exit quietly
        if args.print_env:
            raise SystemExit(0)
        # Otherwise show help and indicate missing command
        parser.print_help(sys.stderr)
        raise SystemExit(2)

    # Run the specified command
    if args.shell:
        # When running through the shell, join the command list into a string
        command_str = " ".join(cmd)
        proc = subprocess.Popen(
            command_str,
            shell=True,
            env=merged,
            stdin=None,
            stdout=None if not args.no_inherit_stdio else subprocess.PIPE,
            stderr=None if not args.no_inherit_stdio else subprocess.PIPE,
        )
    else:
        proc = subprocess.Popen(
            cmd,
            shell=False,
            env=merged,
            stdin=None,
            stdout=None if not args.no_inherit_stdio else subprocess.PIPE,
            stderr=None if not args.no_inherit_stdio else subprocess.PIPE,
        )

    # Stream output if stdio is not inherited
    if args.no_inherit_stdio:
        stream_process(proc)

    proc.wait()
    raise SystemExit(proc.returncode)


if __name__ == "__main__":  # pragma: no cover
    main()