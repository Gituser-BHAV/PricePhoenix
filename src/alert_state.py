
# File: src/alert_state.py
"""Persist alert state and prevent duplicate alerts."""

import json
from pathlib import Path


def load_state(path="data/alert_state.json"):
    """Load saved alert state, or return an empty state."""
    p = Path(path)
    if not p.exists():
        return {}

    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state, path="data/alert_state.json"):
    """Save state atomically to reduce the risk of partial writes."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2), encoding="utf-8")
    tmp.replace(p)


def should_alert(
    state, product_id, alert_type, current_price, reset_price=None
):
    """Alert once per price episode; re-arm after price exceeds reset_price."""
    if current_price is None or current_price <= 0:
        return False

    key = f"{product_id}:{alert_type}"
    entry = state.get(key, {})

    if entry.get("sent"):
        if reset_price is not None and current_price > reset_price:
            # Re-arm now; a later qualifying run may send the next alert.
            state[key] = {"sent": False}
        return False

    return True


def mark_alert_sent(state, product_id, alert_type, current_price):
    """Record that an alert was sent for this product and alert type."""
    state[f"{product_id}:{alert_type}"] = {
        "sent": True,
        "last_price": float(current_price),
    }
