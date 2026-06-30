#!/usr/bin/env python3
"""Add the premium_banner_enabled line to the /api/features return dict in server.py.

Used by solve-workstation to bring a skipped learner to the correct end-state.
Idempotent: if the line is already present, this is a no-op.
Inserts after the new_arrivals_enabled line (works whether ch01 paste is real or stub).
"""
import pathlib
import sys

SERVER_PY = pathlib.Path("/opt/ld/ai-configs-intro/app/server.py")
NEW_LINE = '        "premium_banner_enabled": ld_client.variation("premium-banner", context, False),\n'


def main() -> int:
    text = SERVER_PY.read_text()

    if '"premium_banner_enabled"' in text:
        print("server.py already patched — no action needed.")
        return 0

    anchor = '"new_arrivals_enabled"'
    idx = text.find(anchor)
    if idx == -1:
        print(f"ERROR: anchor '{anchor}' not found in {SERVER_PY}", file=sys.stderr)
        return 1

    end_of_line = text.find("\n", idx) + 1
    new_text = text[:end_of_line] + NEW_LINE + text[end_of_line:]
    SERVER_PY.write_text(new_text)
    print(f"Patched {SERVER_PY}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
