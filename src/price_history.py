import csv
from datetime import datetime, timezone
from pathlib import Path

# File: src/price_history.py
FIELDS = [
    "timestamp",
    "product_id",
    "marketplace",
    "price",
    "currency",
    "in_stock",
]

def read_history(path="data/price_history.csv"):
    file_path = Path(path)
    if not file_path.exists():
        return []
    with file_path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def prices_for_product(rows, product_id):
    prices = []
    for row in rows:
        if row.get("product_id") == product_id:
            try:
                prices.append(float(row["price"]))
            except (TypeError, ValueError, KeyError):
                continue
    return prices

def append_observation(path, product_id, marketplace, price, currency="INR", in_stock=True):
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    exists = file_path.exists()
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "product_id": product_id,
        "marketplace": marketplace,
        "price": f"{float(price):.2f}",
        "currency": currency,
        "in_stock": str(bool(in_stock)).lower()
    }
    with file_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not exists or file_path.stat().st_size == 0:
            writer.writeheader()
        writer.writerow(row)
    return row
