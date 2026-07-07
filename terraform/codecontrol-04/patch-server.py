#!/usr/bin/env python3
"""Add hero_headline to /api/features and wire the /api/track endpoint in server.py.

Used by solve-workstation to bring a skipped learner to the correct end-state.
Idempotent: if the lines are already present, this is a no-op.
"""
import pathlib
import sys

SERVER_PY = pathlib.Path("/opt/ld/ai-configs-intro/app/server.py")

HERO_LINE = '        "hero_headline": ld_client.variation("hero-headline", context, "Wear your features on your sleeve."),\n'

BEGIN_MARKER = "    # ─────────────────────────────────────────────────────────────────────\n    # CodeControl Challenge 04 paste block"
END_MARKER = "    # ─── End CodeControl Challenge 04 paste block ─────────────────────────"

TRACK_CODE = """\
    context = Context.builder(session_id).kind("user").build()
    ld_client.track(event_key, context)
    return {"ok": True}
"""


def main() -> int:
    text = SERVER_PY.read_text()
    changed = False

    # 1. Add hero_headline to the features return dict.
    if '"hero_headline"' not in text:
        for anchor in ['"new_layout_enabled"', '"premium_banner_enabled"', '"new_arrivals_enabled"']:
            idx = text.find(anchor)
            if idx != -1:
                end = text.find("\n", idx) + 1
                text = text[:end] + HERO_LINE + text[end:]
                changed = True
                print(f"Added hero_headline after {anchor}")
                break
        else:
            print("ERROR: no anchor found for hero_headline", file=sys.stderr)
            return 1

    # 2. Replace the /api/track paste block.
    if "ld_client.track(" not in text:
        b = text.find(BEGIN_MARKER)
        e = text.find(END_MARKER)
        if b == -1 or e == -1:
            print("ERROR: Ch04 paste markers not found", file=sys.stderr)
            return 1
        end_of_end_line = text.find("\n", e) + 1
        text = text[:b] + TRACK_CODE + text[end_of_end_line:]
        changed = True
        print("Replaced /api/track paste block")

    if changed:
        SERVER_PY.write_text(text)
        print(f"Patched {SERVER_PY}")
    else:
        print("server.py already patched — no action needed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
