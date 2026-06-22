import shlex
from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedCommand:
    """The result of parsing a raw input string into a command and its arguments."""

    name: str               # e.g. "/tree"  — always lowercased
    args: tuple             # e.g. ("2",)   — zero or more positional strings
    raw: str                # original, unmodified input


class Parser:
    """Splits a raw input string into a ParsedCommand.

    Parsing rules:
    - Leading/trailing whitespace is stripped.
    - Uses shlex.split() to support quoted arguments and escaped quotes.
    - The first token is the command name, lowercased.
    - All remaining tokens are args.
    - Empty input produces an empty name and no args.
    """

    @staticmethod
    def parse(raw: str) -> ParsedCommand:
        stripped = raw.strip()
        if not stripped:
            return ParsedCommand(name="", args=(), raw=raw)

        parts = shlex.split(stripped)
        if not parts:
            return ParsedCommand(name="", args=(), raw=raw)

        name = parts[0].lower()
        args = tuple(parts[1:])
        return ParsedCommand(name=name, args=args, raw=raw)
