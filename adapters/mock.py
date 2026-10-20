import json
from pathlib import Path
from adapters.base import PriceSourceError

def fetch_product(product, path="mock_prices.json"):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        item = data[product["id"]]
        price = float(item["price"])
        if price <= 0:
            raise ValueError("price must be positive")
        return {
            "name": item.get("name", product["name"]),
            "price": price,
            "currency": item.get("currency", "INR"),
            "in_stock": bool(item.get("in_stock", True)),
            "product_url": product["url"]
        }
    except (OSError, KeyError, ValueError, TypeError) as exc:
        raise PriceSourceError(f"Mock data unavailable for {product['id']}: {exc}") from exc
