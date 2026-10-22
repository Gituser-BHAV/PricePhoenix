# scripts/diagnose_product_pages.py — Inspect product-page price metadata

import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "products.json"

def main():
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    products = [p for p in config["products"] if p.get("enabled", True)]

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(
            locale="en-IN",
            viewport={"width": 1365, "height": 900},
        )

        for product in products:
            print(f"\n--- {product['name']} ---")

            try:
                response = page.goto(
                    product["url"],
                    wait_until="domcontentloaded",
                    timeout=45000,
                )

                print("HTTP status:", response.status if response else "No response")
                print("Page title:", page.title())
                print("Final URL:", page.url)

                # Inspect only metadata and product-specific price elements.
                checks = {
                    "OpenGraph price": (
                        'meta[property="product:price:amount"]',
                        "content",
                    ),
                    "Amazon price": (
                        "#corePrice_feature_div .a-offscreen",
                        None,
                    ),
                    "Amazon price block": (
                        "#corePriceDisplay_desktop_feature_div .a-offscreen",
                        None,
                    ),
                    "Generic product price": (
                        '[itemprop="price"]',
                        "content",
                    ),
                }

                found = False

                for label, (selector, attribute) in checks.items():
                    locator = page.locator(selector).first

                    try:
                        if locator.count():
                            value = (
                                locator.get_attribute(attribute)
                                if attribute
                                else locator.inner_text(timeout=2000)
                            )
                            if value and value.strip():
                                print(f"{label}: {value.strip()[:200]}")
                                found = True
                    except Exception:
                        pass

                # Check whether the returned page looks like an interstitial.
                excerpt = re.sub(r"\s+", " ", page.locator("body").inner_text()[:700])
                print("Page excerpt:", excerpt)

                if not found:
                    print(
                        "RESULT: No product-specific price metadata found. "
                        "The page may be an interstitial or omit price data."
                    )

            except Exception as exc:
                print(f"DIAGNOSTIC ERROR: {type(exc).__name__}: {exc}")

        browser.close()

if __name__ == "__main__":
    main()
