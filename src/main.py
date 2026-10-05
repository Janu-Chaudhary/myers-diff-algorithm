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


def forward_pass(a, b):
    """Run Myers' greedy search on sequences a and b; return the saved V slices ("trace").

    Edit graph: x counts items of a used up, y counts items of b. A move right (x+1) deletes
    a[x]; a move down (y+1) inserts b[y]; a diagonal move (x+1, y+1) keeps an equal item for free.
    Diagonal k = x - y. With d edits, only diagonals -d, -d+2, ..., d can be reached.
    v[k] holds the furthest x reached so far on diagonal k (then y = x - k).

    trace[d] is a copy of v[-d..d] taken after round d; its index i stands for diagonal i - d.
    The search stops in the first round d that reaches (len(a), len(b)), so len(trace) - 1 is
    the minimal number of edits D. Works on any sequences of comparable items: lines or characters.
    """
    n, m = len(a), len(b)
    max_d = n + m                      # worst case: delete all of a, insert all of b
    offset = max_d                     # python lists cannot use negative k, so v[k] is v[k + offset]
    v = [0] * (2 * max_d + 2)          # room for k = -max_d .. max_d + 1 (k + 1 is read at k = d)
    trace = []
    # v[1] = 0 is a virtual start: round d = 0 "moves down" from diagonal 1 to land on (0, 0).
    for d in range(max_d + 1):
        for k in range(-d, d + 1, 2):
            # Choose where to come from. Down from k+1 (insert) if that diagonal got further,
            # otherwise right from k-1 (delete). On a tie we go right, so deletions come first.
            # k == -d has no k-1 neighbour; k == d has no k+1 neighbour.
            if k == -d or (k != d and v[offset + k - 1] < v[offset + k + 1]):
                x = v[offset + k + 1]          # down: x stays, y grows by one
            else:
                x = v[offset + k - 1] + 1      # right: x grows by one
            y = x - k
            # Follow the snake: equal items are free diagonal moves.
            while x < n and y < m and a[x] == b[y]:
                x += 1
                y += 1
            v[offset + k] = x                  # furthest-reaching point on diagonal k
            if x >= n and y >= m:              # reached the bottom-right corner: d is minimal
                trace.append(v[offset - d:offset + d + 1])
                return trace
        # Save only diagonals -d..d (2d+1 numbers), never the whole v (assignment §4).
        trace.append(v[offset - d:offset + d + 1])
    # No return needed here: by d = max_d the corner is always reached.


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


# Run only when started as a program, so tests can import the functions above without running main().
if __name__ == "__main__":
    raise SystemExit(main())
