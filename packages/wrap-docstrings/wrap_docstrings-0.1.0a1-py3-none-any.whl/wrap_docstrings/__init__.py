"""Tool for wrapping docstrings."""

import argparse
import sys
import textwrap
from pathlib import Path

__all__ = ["wrap_docstrings"]


def wrap_docstrings(text: str, width: int, indent: int) -> str:
    """Wraps the Google-style docstrings in a given piece of text.

    Args:
        text: The input text.
        width: Text width for wrapping the docstring.
        indent: Indent width for the code, e.g., 2 or 4 spaces.
    """
    # Disable if this comment is in the file.
    if "# wrap-docstrings: disable\n" in text:
        return text

    lines = text.splitlines(keepends=True)
    final_lines = []

    # Indicates that we are within the "Args:" section of the docstring. It's assumed
    # the section already follows Google-style.
    is_args_section = False

    # Indentation of the current argument section -- this is the indent of the "Args:"
    # header plus the indent given above.
    cur_indent = 0

    # Lines of text for the current argument, all stripped.
    arg_lines = []

    for line in lines:
        stripped = line.strip()
        line_indent = len(line) - len(line.lstrip())

        if is_args_section:
            # Here we are in an args section, so we just need to build the string for
            # the current arg and write it when necessary.

            # We're at the start of a new argument.
            starting_new_arg = line_indent == cur_indent

            # All args sections are assumed to end with blank line or triple quotes.
            end_args_section = stripped in ("", '"""')

            if (starting_new_arg or end_args_section) and len(arg_lines) > 0:
                # Write the current argument's docstring to the output.
                final_lines.append(
                    textwrap.fill(
                        " ".join(arg_lines),
                        width=width,
                        initial_indent=cur_indent * " ",
                        subsequent_indent=(cur_indent + indent) * " ",
                        break_long_words=False,
                        break_on_hyphens=False,
                    )
                    + "\n"
                )
                arg_lines.clear()

            if end_args_section:
                is_args_section = False
                final_lines.append(line)
            else:
                arg_lines.append(stripped)

        elif stripped == "Args:":
            is_args_section = True

            # Indentation of this section's args.
            cur_indent = line_indent + indent

            final_lines.append(line)

        else:
            final_lines.append(line)

    final_text = "".join(final_lines)
    return final_text


def format_file(file: Path, width: int, indent: int) -> None:
    """Formats a single file."""
    text = file.read_text()
    final_text = wrap_docstrings(text, width=width, indent=indent)
    file.write_text(final_text)


def main() -> None:
    """Wraps args in Google-style docstrings."""
    parser = argparse.ArgumentParser(
        prog="wrap-docstrings", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "path",
        help="Input file or directory, or '-' to read from stdin and write to stdout",
    )
    parser.add_argument(
        "-w",
        "--width",
        type=int,
        default=88,
        required=False,
        help="Text width for wrapping the docstring.",
    )
    parser.add_argument(
        "-i",
        "--indent",
        type=int,
        default=4,
        required=False,
        help="Indent width for the code, e.g., 2 or 4 spaces.",
    )
    args = parser.parse_args()

    if args.path == "-":
        text = sys.stdin.read()
        final_text = wrap_docstrings(text, width=args.width, indent=args.indent)
        sys.stdout.write(final_text)
    else:
        path = Path(args.path)
        if path.is_dir():
            for f in path.rglob("*.py"):
                format_file(f, args.width, args.indent)
            print(f"Formatted Python files in directory {path}")
        elif path.is_file() and path.suffix == ".py":
            format_file(path, args.width, args.indent)
            print(f"Formatted {path}")
        else:
            print(f"Skipping since {path} is not a Python file.")
