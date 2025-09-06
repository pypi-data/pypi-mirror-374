
import argparse, json, os, sys, subprocess
from typing import Dict, List
from dotenv import dotenv_values

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="env-injector",
        description="Inject env vars into a spawned process."
    )
    # Sources
    p.add_argument("-e", "--env", action="append", default=[], metavar="KEY=VAL",
                   help="Set an env var (repeatable). Example: -e FOO=bar -e X=1")
    p.add_argument("-f", "--file", action="append", default=[],
                   help="Load vars from a .env-like file (repeatable). Default also tries ./.env")
    p.add_argument("--profile", action="append", default=[],
                   help="Profile name(s) to load .env.<profile> (repeatable). Example: --profile dev --profile local")

    # Behavior / merging semantics
    p.add_argument("--order", default="system,file,flags",
                   help=("Comma-separated sources from low→high priority (rightmost wins). "
                         "Valid tokens: system,file,flags. Default: system,file,flags"))
    p.add_argument("-o", "--override", action="store_true",
                   help="Legacy mode: apply additions over system env (flags win over file). Ignored if --order is set explicitly.")
    p.add_argument("--unset", action="append", default=[], metavar="KEY",
                   help="Unset/remove variable(s) before spawning (repeatable)")

    # Output / dry-run
    p.add_argument("--print-env", action="store_true",
                   help="Print merged env as KEY=VAL lines before running")
    p.add_argument("--json", action="store_true",
                   help="Print merged env as JSON and exit (does NOT run the command)")

    # Process execution
    p.add_argument("-s", "--shell", action="store_true",
                   help="Run using a shell (be careful with quoting)")
    p.add_argument("--no-inherit-stdio", action="store_true",
                   help="Do not inherit stdio; stream output instead")
    p.add_argument("--", dest="double_dash", action="store_true",
                   help=argparse.SUPPRESS)
    p.add_argument("command", nargs=argparse.REMAINDER,
                   help="Command to run (prefix with -- to disambiguate)")

    return p

def parse_pairs(pairs: List[str]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise SystemExit(f"Invalid --env value (expected KEY=VAL): {pair}")
        k, v = pair.split("=", 1)
        k = k.strip()
        if not k:
            raise SystemExit(f"Invalid key in: {pair}")
        out[k] = v
    return out

def load_files(files: List[str], profiles: List[str]) -> Dict[str, str]:
    """
    Load variables from: explicit --file entries, then default .env (if present),
    plus any .env.<profile> for each --profile (if present).
    Later loads do NOT automatically override earlier loads here; precedence is handled in merge().
    We just return a single mapping from all discovered files; later items in this function
    overwrite earlier ones so that a single 'file' source has self-consistent precedence:
    .env -> .env.<profile1> -> .env.<profile2> -> explicit --file (last one wins)
    """
    discovered: List[str] = []

    # base .env (if present)
    if os.path.exists(".env"):
        discovered.append(".env")

    # profiles: .env.<profile>
    for prof in profiles:
        path = f".env.{prof}"
        if os.path.exists(path):
            discovered.append(path)

    # explicit files last (highest within 'file' source)
    for f in files:
        if os.path.exists(f):
            discovered.append(f)
        else:
            raise SystemExit(f"--file not found: {f}")

    result: Dict[str, str] = {}
    for path in discovered:
        vals = dotenv_values(path)
        for k, v in vals.items():
            if v is not None:
                result[k] = str(v)
    return result

def normalize_order(order: str) -> List[str]:
    tokens = [t.strip().lower() for t in order.split(",") if t.strip()]
    valid = {"system", "file", "flags"}
    if any(t not in valid for t in tokens) or len(tokens) != len(set(tokens)) or not tokens:
        raise SystemExit("--order must be a comma list using each of: system,file,flags exactly once")
    # Ensure it contains exactly all three
    if set(tokens) != valid:
        raise SystemExit("--order must include exactly: system,file,flags")
    return tokens

def merge_env(system: Dict[str, str], filemap: Dict[str, str], flags: Dict[str, str], order: List[str]) -> Dict[str, str]:
    """
    Merge sources from low→high priority (rightmost wins overall).
    'order' is a permutation of ['system','file','flags'].
    """
    layers = {
        "system": dict(system),
        "file": dict(filemap),
        "flags": dict(flags),
    }
    merged: Dict[str, str] = {}
    # apply in given order; later sources override earlier keys
    for src in order:
        merged.update(layers[src])
    return merged

def apply_unset(envmap: Dict[str, str], keys: List[str]) -> Dict[str, str]:
    if not keys: return envmap
    env = dict(envmap)
    for k in keys:
        env.pop(k, None)
    return env

def stream_process(proc: subprocess.Popen):
    try:
        if proc.stdout:
            for line in iter(proc.stdout.readline, b""):
                sys.stdout.buffer.write(line)
        if proc.stderr:
            for line in iter(proc.stderr.readline, b""):
                sys.stderr.buffer.write(line)
    except KeyboardInterrupt:
        pass

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Handle command after "--"
    cmd = args.command
    if cmd and cmd[0] == "--":
        cmd = cmd[1:]

    # Build sources
    flags_map = parse_pairs(args.env)
    files_map = load_files(args.file, args.profile)

    # Determine precedence
    order = normalize_order(args.order) if "order" in args and args.order else ["system","file","flags"]

    # Back-compat: if user explicitly passed --override *and* didn't customize --order,
    # make flags > file > system by forcing order (already default). We keep the flag for compatibility messaging.
    # (We document that --order takes precedence over --override.)
    if args.override and args.order == "system,file,flags":
        order = ["system", "file", "flags"]

    # Merge + post-processing
    merged = merge_env(os.environ, files_map, flags_map, order)
    merged = apply_unset(merged, args.unset)

    # Output modes
    if args.json:
        print(json.dumps(merged, ensure_ascii=False, indent=2))
        raise SystemExit(0)

    if args.print_env:
        for k, v in merged.items():
            # Print in a predictable order
            print(f"{k}={v}")

    # If no command, stop here if user only wanted printing
    if not cmd:
        if args.print_env:
            raise SystemExit(0)
        parser.print_help(sys.stderr)
        raise SystemExit(2)

    # Run command
    if args.shell:
        # User handles quoting; join tokens with spaces
        command_str = " ".join(cmd)
        proc = subprocess.Popen(
            command_str, shell=True, env=merged,
            stdin=None,
            stdout=None if not args.no_inherit_stdio else subprocess.PIPE,
            stderr=None if not args.no_inherit_stdio else subprocess.PIPE
        )
    else:
        proc = subprocess.Popen(
            cmd, shell=False, env=merged,
            stdin=None,
            stdout=None if not args.no_inherit_stdio else subprocess.PIPE,
            stderr=None if not args.no_inherit_stdio else subprocess.PIPE
        )

    if args.no_inherit_stdio:
        stream_process(proc)

    proc.wait()
    raise SystemExit(proc.returncode)

if __name__ == "__main__":
    main()
