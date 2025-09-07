import ast
import sys
import json
from typing import Any
from .mojangson import *

from argparse import (
    Namespace,
    ArgumentParser
)


def read_input(args: Namespace) -> str:
    """
    Read the input Mojangson string from a file or direct argument.

    Args:
        args (Namespace): Parsed command-line arguments.

    Returns:
        str: The Mojangson input string.

    Exits:
        Exits the program if neither file nor input string is provided.
    """
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            return f.read()
    elif args.input:
        return args.input
    else:
        print("Error: you must provide a string or use -f/--file", file=sys.stderr)
        sys.exit(1)


def write_output(args: Namespace, content: Any) -> None:
    """
    Write output to a file or print to stdout.

    Args:
        args (Namespace): Parsed command-line arguments.
        content (Any): The content to output; will be converted to string if necessary.
    """
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            if isinstance(content, str):
                f.write(content)
            else:
                f.write(json.dumps(content, ensure_ascii=False))
    else:
        print(content)


def main() -> None:
    """
    Entry point for the Mojangson CLI.

    Parses command-line arguments, reads input, executes the selected command
    (parse, stringify, simplify, normalize), and outputs the result.
    """
    parser = ArgumentParser(
        prog="mojangson",
        description="CLI for working with Mojangson (parse, stringify, simplify, normalize)"
    )
    parser.add_argument(
        "command",
        choices=["parse", "stringify", "simplify", "normalize"],
        help="Command to execute"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Mojangson string (if not using -f/--file)"
    )
    parser.add_argument(
        "-f", "--file",
        help="Path to input file"
    )
    parser.add_argument(
        "-o", "--output",
        help="Path to output file"
    )
    
    args = parser.parse_args()
    text = read_input(args)

    if args.command == "parse":
        result = parse(text)
    elif args.command == "stringify":
        result = stringify(ast.literal_eval(text))
    elif args.command == "simplify":
        result = simplify(ast.literal_eval(text))
    elif args.command == "normalize":
        result = normalize(text)
    else:
        parser.error(f"Unknown command {args.command}")
    
    write_output(args, result)
