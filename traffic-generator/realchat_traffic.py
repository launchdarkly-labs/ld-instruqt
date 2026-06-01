#!/usr/bin/env python3
"""Real /chat traffic for online-judge labs (Evaluate ch02 and later).

Reads short shopper questions from messages.txt and POSTs them to the
local ToggleWear /chat endpoint in a loop, so attached judges have real
Otto responses to grade.

Different from background_traffic.py — that one emits synthetic LD
metric events without touching Bedrock; this one drives real /chat
calls so the SDK's auto-evaluation path (attached built-in or custom
judges sampling at their configured rate) actually fires.

Exits cleanly on SIGTERM/SIGINT. Safe to launch with nohup and kill
with `pkill -f realchat_traffic.py`.

Environment variables (all optional):
  CHAT_URL       default http://localhost:3000/chat
  MIN_SLEEP      default 2.0  -- min seconds between requests
  MAX_SLEEP      default 4.0  -- max seconds between requests
  PREMIUM_RATIO  default 0.2  -- fraction of requests sent with tier=premium
"""
from __future__ import annotations

import json
import os
import random
import signal
import sys
import time
import uuid
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

MESSAGES_FILE = Path(__file__).resolve().parent / "messages.txt"
CHAT_URL = os.getenv("CHAT_URL", "http://localhost:3000/chat")
MIN_SLEEP = float(os.getenv("MIN_SLEEP", "2"))
MAX_SLEEP = float(os.getenv("MAX_SLEEP", "4"))
PREMIUM_RATIO = float(os.getenv("PREMIUM_RATIO", "0.2"))


def load_messages() -> list[str]:
    messages: list[str] = []
    with MESSAGES_FILE.open() as f:
        for raw in f:
            line = raw.strip()
            if line and not line.startswith("#"):
                messages.append(line)
    return messages


def post_chat(message: str, tier: str, session_id: str) -> int:
    payload = json.dumps({
        "message": message,
        "user_tier": tier,
        "session_id": session_id,
    }).encode()
    req = Request(
        CHAT_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(req, timeout=30) as resp:
        return resp.status


def run() -> None:
    messages = load_messages()
    if not messages:
        print("realchat_traffic: no messages loaded", file=sys.stderr)
        sys.exit(1)

    stop = False

    def handle_signal(_signum, _frame) -> None:
        nonlocal stop
        stop = True

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    while not stop:
        msg = random.choice(messages)
        tier = "premium" if random.random() < PREMIUM_RATIO else "free"
        session = f"realchat-{uuid.uuid4().hex[:8]}"
        try:
            status = post_chat(msg, tier, session)
            print(f"[{status}] tier={tier} msg={msg!r}", flush=True)
        except URLError as e:
            print(f"[err] {e}", file=sys.stderr, flush=True)
        time.sleep(random.uniform(MIN_SLEEP, MAX_SLEEP))


if __name__ == "__main__":
    run()
