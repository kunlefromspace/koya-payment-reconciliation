#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
import json
from datetime import datetime

latest = {}  # txn_id -> ((timestamp, file_order), event)

with open("payments.jsonl", encoding="utf-8") as f:
    for order, line in enumerate(f):
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue  # unreadable (truncated/corrupt) line
        if not isinstance(event, dict):
            continue
        txn_id = event.get("txn_id")
        if txn_id is None or txn_id == "":
            continue  # no txn_id
        try:
            ts = datetime.fromisoformat(event["ts"].replace("Z", "+00:00"))
        except (KeyError, AttributeError, ValueError):
            continue
        # Only the latest attempt per txn_id counts. Export order is not
        # chronological, so compare timestamps (file order breaks exact ties).
        key = (ts, order)
        if txn_id not in latest or key > latest[txn_id][0]:
            latest[txn_id] = (key, event)


def parse_amount(value):
    if isinstance(value, str):
        value = value.replace(",", "").strip()
    return float(value)


total = 0.0
count = 0
for _, event in latest.values():
    if event.get("status") == "success":
        total += parse_amount(event["amount"])
        count += 1

with open("expected.txt") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")