"""Myers diff: print a minimal line diff of two files (Part A) and changed-character ranges (Part B).

Usage:  python3 main.py lines A B       line diff of file A to file B
        python3 main.py highlight A B   the same diff, plus a "?" line of changed characters

Algorithm: Eugene Myers, "An O(ND) Difference Algorithm and Its Variations" (1986), section 3.
"""

import sys


def read_lines(path):
    """Read a file and return its lines as a list of bytes objects (assignment §1).

    The file is read as raw bytes, never as text: text mode would turn b"\\r\\n" into b"\\n",
    and some test files contain bytes that are not valid UTF-8.
    Split on the newline byte. If the last piece is empty, drop it, so a final newline does not
    create an extra empty line and an empty file has no lines. Any b"\\r" stays inside its line.
    Raises OSError if the file cannot be read; main() turns that into exit code 2.
    """
    with open(path, "rb") as file:
        lines = file.read().split(b"\n")
    if lines[-1] == b"":
        lines.pop()
    return lines


def main() -> int:
    if len(sys.argv) != 4 or sys.argv[1] not in ("lines", "highlight"):
        print("usage: main.py lines|highlight A_PATH B_PATH", file=sys.stderr)
        return 2
    command, a_path, b_path = sys.argv[1:]

    # Read both files before printing anything, so an unreadable file leaves stdout empty.
    # OSError covers every way a read can fail: missing file, a folder, no permission.
    try:
        a_lines = read_lines(a_path)
        b_lines = read_lines(b_path)
    except OSError as error:
        print(f"error: cannot read input file: {error}", file=sys.stderr)
        return 2
    return 0


raise SystemExit(main())
