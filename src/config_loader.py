import json
from pathlib import Path

def load_config(path="config/products.json"):
    with open(path, "r", encoding="utf-8") as f:
        config = json.load(f)

    if not isinstance(config.get("products"), list):
        raise ValueError("'products' must be a list")

    seen = set()
    for product in config["products"]:
        for key in ("id", "name", "url", "source", "target_price", "enabled"):
            if key not in product:
                raise ValueError(f"Product is missing required field: {key}")
        if product["id"] in seen:
            raise ValueError(f"Duplicate product id: {product['id']}")
        seen.add(product["id"])
        if not isinstance(product["target_price"], (int, float)) or product["target_price"] <= 0:
            raise ValueError(f"Invalid target_price for {product['id']}")
        if product["source"] not in {"mock", "amazon", "flipkart"}:
            raise ValueError(f"Unsupported source for {product['id']}: {product['source']}")
    return config
