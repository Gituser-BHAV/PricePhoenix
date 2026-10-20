import argparse
import os
from pathlib import Path

from adapters.base import PriceSourceError
from adapters.mock import fetch_product as fetch_mock
from adapters.amazon import fetch_product as fetch_amazon
from adapters.flipkart import fetch_product as fetch_flipkart
from src.config_loader import load_config
from src.price_history import read_history, prices_for_product, append_observation
from src.recommendation_engine import recommend
from src.alert_state import load_state, save_state, should_alert, mark_alert_sent
from src.email_notifier import email_is_configured, send_email

def run(mock=False):
    config = load_config()
    settings = config.get("settings", {})
    history_path = "data/price_history.csv"
    state_path = "data/alert_state.json"
    history_rows = read_history(history_path)
    state = load_state(state_path)
    had_error = False

    for product in config["products"]:
        if not product.get("enabled", True):
            continue
        source = "mock" if mock else product["source"]
        fetcher = {"mock": fetch_mock, "amazon": fetch_amazon, "flipkart": fetch_flipkart}.get(source)
        if fetcher is None:
            print(f"[ERROR] {product['id']}: unsupported source {source}")
            had_error = True
            continue

        try:
            item = fetcher(product)
            price = float(item["price"])
            if price <= 0:
                raise PriceSourceError("Returned price is not positive")
            if item.get("currency", "INR") != settings.get("currency", "INR"):
                raise PriceSourceError("Returned currency does not match configured currency")
        except Exception as exc:
            print(f"[ERROR] {product['id']}: {exc}")
            had_error = True
            continue

        prior_prices = prices_for_product(history_rows, product["id"])
        append_observation(
            history_path, product["id"], source, price,
            item.get("currency", "INR"), item.get("in_stock", True)
        )
        recommendation = recommend(price, float(product["target_price"]), prior_prices, settings)
        print(f"\n{item.get('name', product['name'])}")
        print(f"  Source: {source}")
        print(f"  Current: ₹{price:,.2f} | Target: ₹{float(product['target_price']):,.2f}")
        print(f"  Recommendation: {recommendation['label']} — {recommendation['reason']}")

        alert_type = None
        if settings.get("alert_on_target", True) and price <= float(product["target_price"]):
            alert_type = "target"
        elif settings.get("alert_on_good_deal", True) and recommendation["label"] == "GOOD DEAL":
            alert_type = "good_deal"
        elif product.get("alert_threshold") is not None and price <= float(product["alert_threshold"]):
            alert_type = "near_target"

        if alert_type:
            reset_price = float(product.get("alert_threshold", product["target_price"])) * 1.03
            if should_alert(state, product["id"], alert_type, price, reset_price):
                subject = f"[PricePhoenix] {alert_type.replace('_', ' ').title()}: {item.get('name', product['name'])}"
                body = (
                    f"Product: {item.get('name', product['name'])}\n"
                    f"Marketplace/source: {source}\n"
                    f"Current price: ₹{price:,.2f}\n"
                    f"Target price: ₹{float(product['target_price']):,.2f}\n"
                    f"Recommendation: {recommendation['label']}\n"
                    f"Reason: {recommendation['reason']}\n"
                    f"Product link: {product['url']}\n"
                )
                if settings.get("email_alerts", True) and os.getenv("EMAIL_ENABLED", "").lower() == "true":
                    if email_is_configured():
                        try:
                            send_email(subject, body)
                            print("  Email: sent")
                            mark_alert_sent(state, product["id"], alert_type, price)
                        except Exception as exc:
                            print(f"  [EMAIL ERROR] {exc}")
                            had_error = True
                    else:
                        print("  Email: not sent (SMTP secrets missing)")
                else:
                    print("  Email: disabled; alert printed only")
                if not (settings.get("email_alerts", True) and os.getenv("EMAIL_ENABLED", "").lower() == "true" and email_is_configured()):
                    # In dry/mock testing, do not mark the alert as sent.
                    pass

    save_state(state, state_path)
    if had_error:
        print("\nFinished with one or more errors. Check the logs.")
    else:
        print("\nFinished successfully.")
    return 1 if had_error else 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PricePhoenix price tracker")
    parser.add_argument("--mock", action="store_true", help="Force mock prices for all enabled products")
    args = parser.parse_args()
    raise SystemExit(run(mock=args.mock))
