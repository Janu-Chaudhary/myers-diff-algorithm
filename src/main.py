"""Myers diff: print a minimal line diff of two files (Part A) and changed-character ranges (Part B).

Usage:  python3 main.py lines A B       line diff of file A to file B
        python3 main.py highlight A B   the same diff, plus a "?" line of changed characters

Algorithm: Eugene Myers, "An O(ND) Difference Algorithm and Its Variations" (1986), section 3.

Flow: read_lines -> forward_pass (find D, save V) -> backtrack (edit script) -> deletes_first
(output rows) -> for highlight only, add_question_rows (pairs lines, calls changed_ranges, which
runs the same forward_pass and backtrack on characters) -> one write to stdout.
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

    trace[d] is a copy of v[-d..d] taken after round d; position p in it stands for diagonal p - d.
    The search stops in the first round d that reaches (len(a), len(b)), so len(trace) - 1 is
    the minimal number of edits D. Works on any sequences of comparable items: lines or characters.
    """
    n, m = len(a), len(b)
    max_d = n + m                      # worst case: delete all of a, insert all of b
    offset = max_d                     # python lists cannot use negative k, so v[k] is v[k + offset]
    v = [0] * (2 * max_d + 2)          # room for k = -max_d .. max_d + 1 (k + 1 is read at k = d)
    trace = []
    # Virtual start: diagonal 1 (v[offset + 1]) holds x = 0, so round d = 0 "moves down" from it
    # and lands on (0, 0).
    for d in range(max_d + 1):
        for k in range(-d, d + 1, 2):
            i = offset + k                     # where diagonal k lives in v; i-1 is k-1, i+1 is k+1
            # Choose where to come from. Down from k+1 (insert) if that diagonal got further,
            # otherwise right from k-1 (delete). On a tie we go right, so deletions come first.
            # k == -d has no k-1 neighbour; k == d has no k+1 neighbour.
            if k == -d or (k != d and v[i - 1] < v[i + 1]):
                x = v[i + 1]                   # down: x stays, y grows by one
            else:
                x = v[i - 1] + 1               # right: x grows by one
            y = x - k
            # Follow the snake: equal items are free diagonal moves.
            while x < n and y < m and a[x] == b[y]:
                x += 1
                y += 1
            v[i] = x                           # furthest-reaching point on diagonal k
            if x >= n and y >= m:              # reached the bottom-right corner: d is minimal
                trace.append(v[offset - d:offset + d + 1])
                return trace
        # Save only diagonals -d..d (2d+1 numbers), never the whole v (assignment §4).
        trace.append(v[offset - d:offset + d + 1])
    # No return needed here: by d = max_d the corner is always reached.


def backtrack(trace, n, m):
    """Recover the edit script from forward_pass's trace for sequences of lengths n and m.

    Returns a list of operations in order from the start of the files:
    " " keeps the next item of a (equal to the next of b), "-" deletes the next item of a,
    "+" inserts the next item of b.
    Walks from the corner (n, m) back to (0, 0). In round d, the saved slice of round d - 1
    shows which neighbour diagonal the forward pass came from, using the same rule it used.
    """
    x, y = n, m
    ops = []
    for d in range(len(trace) - 1, 0, -1):
        k = x - y
        prev = trace[d - 1]                    # v[-(d-1)..d-1]; diagonal j is at index j + d - 1
        # Same choice as the forward pass: down from k+1 (insert) or right from k-1 (delete).
        if k == -d or (k != d and prev[k - 1 + d - 1] < prev[k + 1 + d - 1]):
            prev_k, op = k + 1, "+"
        else:
            prev_k, op = k - 1, "-"
        prev_x = prev[prev_k + d - 1]          # where round d - 1 ended on that diagonal
        prev_y = prev_x - prev_k
        # Walk back along the snake: diagonal moves are kept items.
        while x > prev_x and y > prev_y:
            ops.append(" ")
            x -= 1
            y -= 1
        ops.append(op)                         # the single insert or delete of round d
        x, y = prev_x, prev_y
    # Round 0 is only a snake from (0, 0), so the rest are kept items (here x == y):
    # add x keep operations (" " * x is a string of x spaces; extend adds each one).
    ops.extend(" " * x)
    ops.reverse()                              # collected from the end; one reverse, no insert(0, ...)
    return ops


def deletes_first(a, b, ops):
    """Turn the edit script into output rows (prefix, item), deletions first in every change block.

    A change block is a run of "-" and "+" with no keep between them (assignment §2). The
    backtrack can mix them inside a block, so each block's deletes and inserts are held back
    and written out as all deletes, then all inserts, when the block ends. This stays a valid
    diff: deletes only use items of a and inserts only items of b, each still in order.
    """
    rows, deletes, inserts = [], [], []
    i = j = 0                                  # next unused item of a and of b
    for op in ops:
        if op == " ":
            rows += deletes + inserts          # a keep ends the current change block
            deletes, inserts = [], []
            rows.append((b" ", a[i]))
            i += 1
            j += 1
        elif op == "-":
            deletes.append((b"-", a[i]))
            i += 1
        else:
            inserts.append((b"+", b[j]))
            j += 1
    rows += deletes + inserts                  # the last block, if the files end with changes
    return rows


def mark(ranges, position):
    """Add one changed character to a list of [start, end) ranges, merging with the last if touching."""
    if ranges and ranges[-1][1] == position:
        ranges[-1][1] = position + 1           # touches the previous range: extend it
    else:
        ranges.append([position, position + 1])


def format_ranges(ranges):
    """Write ranges as "3-5,9-12", or "." when nothing changed on this side (assignment §3)."""
    return ",".join(f"{start}-{end}" for start, end in ranges) or "."


def changed_ranges(old, new):
    """Return (old ranges, new ranges) as text for one paired '-' line and '+' line (assignment §3).

    Part B is Myers again, one level down: the items are the characters (Unicode code points)
    of the two lines instead of the lines of two files. Deleted characters are the changed
    ranges of the old line, inserted characters those of the new line. Because Myers finds
    the fewest edits, the number of highlighted characters is the minimum possible.
    """
    old_text, new_text = old.decode("utf-8"), new.decode("utf-8")   # code points: emoji = 1, \r = 1
    ops = backtrack(forward_pass(old_text, new_text), len(old_text), len(new_text))
    old_ranges, new_ranges = [], []
    i = j = 0                                  # position in the old line and in the new line
    for op in ops:
        if op == "-":
            mark(old_ranges, i)
        elif op == "+":
            mark(new_ranges, j)
        if op != "+":                          # keep and delete use up one old character
            i += 1
        if op != "-":                          # keep and insert use up one new character
            j += 1
    return format_ranges(old_ranges), format_ranges(new_ranges)


def add_question_rows(rows):
    """Return rows with a "?" row after every paired "+" row, for the highlight command (§3).

    Inside a change block the 1st "-" pairs with the 1st "+", the 2nd with the 2nd, and so on;
    leftover lines on either side get no "?" row. This relies on deletes_first(): in every block
    all "-" rows come before any "+" row, so the partners are known when each "+" is reached.
    """
    out = []
    deletes = []                               # "-" lines of the current change block
    inserts_seen = 0                           # "+" lines seen so far in the current block
    for prefix, line in rows:
        out.append((prefix, line))
        if prefix == b" ":
            deletes, inserts_seen = [], 0      # a keep ends the change block
        elif prefix == b"-":
            deletes.append(line)
        else:
            if inserts_seen < len(deletes):    # this "+" has a partner: the "-" at the same index
                old_ranges, new_ranges = changed_ranges(deletes[inserts_seen], line)
                out.append((b"?", f" {old_ranges} | {new_ranges}".encode()))
            inserts_seen += 1
    return out


def main() -> int:
    """Run one command on two files; return the exit code (0 = success, 2 = bad usage or unreadable file)."""
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

    ops = backtrack(forward_pass(a_lines, b_lines), len(a_lines), len(b_lines))
    rows = deletes_first(a_lines, b_lines, ops)
    if command == "highlight":
        rows = add_question_rows(rows)        # Part B: same diff plus "?" rows
    # Lines are bytes (they may hold \r or invalid UTF-8), so write bytes to stdout's binary buffer.
    # writelines streams the lines out one by one through the buffer, instead of first joining the
    # whole output into one big copy: on 500,000 long lines that copy alone cost ~200 MiB (§4: 768 MiB).
    sys.stdout.buffer.writelines(prefix + line + b"\n" for prefix, line in rows)
    return 0


# Run only when started as a program, so tests can import the functions above without running main().
if __name__ == "__main__":
    raise SystemExit(main())
