import json
import pytest
from src.config_loader import load_config

def test_example_config_loads():
    config = load_config("config/products.json")
    assert len(config["products"]) >= 1

def test_duplicate_ids_rejected(tmp_path):
    p = tmp_path / "products.json"
    p.write_text(json.dumps({"products": [
        {"id":"x","name":"A","url":"https://example.com/a","source":"mock","target_price":1,"enabled":True},
        {"id":"x","name":"B","url":"https://example.com/b","source":"mock","target_price":2,"enabled":True}
    ]}), encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate"):
        load_config(p)
