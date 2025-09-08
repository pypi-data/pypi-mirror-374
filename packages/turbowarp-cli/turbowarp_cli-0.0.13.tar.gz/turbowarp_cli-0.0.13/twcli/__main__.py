import argparse
from typing import Optional
from pathlib import Path

from twcli import run
from twcli import __version__


class Args(argparse.Namespace):
    command: Optional[str]
    project: Optional[str]
    input: Optional[list[str]]
    headed: Optional[bool]
    raise_status: Optional[bool]

def main():
    parser = argparse.ArgumentParser(
        prog="twcli",
        description="Run scratch projects in your terminal using turbowarp scaffolding",
        epilog=f"{__version__=}"
    )

    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", description="run a scratch project")
    run_parser.add_argument("project", help="Project path")
    run_parser.add_argument("-i", "--input", nargs="*", dest="input", help="Project input for ask blocks")
    run_parser.add_argument("-H", "--headed", action="store_true", dest="headed", help="Whether to disable headless mode")
    run_parser.add_argument("-R", "--raise", action="store_true", dest="raise_status", help="Whether to trigger an error if the exit code != '0'")

    args = parser.parse_args(namespace=Args())

    match args.command:
        case "run":
            path = Path(args.project).resolve()
            assert path.exists(), f"Could not find project at {path}"

            print(f"Running {path}")

            project_input = None
            if args.input is not None:
                project_input = '\n'.join(args.input)

            print(f"Args: {project_input!r}")

            ret = run(path.read_bytes(), project_input, headless=not args.headed)[-1]
            code = ret["content"] if ret["type"] == "exit_code" else "0"

            if args.raise_status:
                if code != "0":
                    raise RuntimeError(code)

            exit(code)
