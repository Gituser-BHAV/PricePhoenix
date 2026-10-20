import json
from pathlib import Path

def load_state(path="data/alert_state.json"):
    p = Path(path)
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state, path="data/alert_state.json"):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2), encoding="utf-8")
    tmp.replace(p)

def should_alert(state, product_id, alert_type, current_price, reset_price=None):
    """Alert once per active price episode; re-arm when price rises above reset_price."""
    key = f"{product_id}:{alert_type}"
    entry = state.get(key, {})
    if entry.get("sent"):
        if reset_price is not None and current_price > reset_price:
            # Re-arm for a future drop, but do not alert on the reset run itself.
            state[key] = {"sent": False}
            return False
        return False
    return True

def mark_alert_sent(state, product_id, alert_type, current_price):
    state[f"{product_id}:{alert_type}"] = {"sent": True, "last_price": float(current_price)}
