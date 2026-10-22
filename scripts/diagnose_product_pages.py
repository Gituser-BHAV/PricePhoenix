
# File: scripts/diagnose_product_pages.py
"""Check whether GitHub Actions can open product pages and see price text."""

import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "products.json"

PRICE_PATTERN = re.compile(
    r"(?:₹|Rs\.?\s*)\s?[\d,]+(?:\.\d{1,2})?"
)

BLOCK_MARKERS = (
    "captcha",
    "robot check",
    "access denied",
    "unusual traffic",
    "verify you are human",
    "automated access",
)


def main():
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    products = [p for p in config["products"] if p.get("enabled", True)]

    if not products:
        print("No enabled products found in config/products.json")
        return

    failures = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            locale="en-IN",
            timezone_id="Asia/Kolkata",
        )

        for product in products:
            name = product.get("name", product.get("id", "Unknown"))
            url = product["url"]

            print(f"\n--- {name} ---")
            try:
                response = page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=45000,
                )
                page.wait_for_timeout(4000)

                status = response.status if response else "no HTTP response"
                title = page.title()
                final_url = page.url
                body = page.locator("body").inner_text(timeout=10000)
                excerpt = " ".join(body.split())[:1200]

                print(f"HTTP status: {status}")
                print(f"Page title: {title}")
                print(f"Final URL: {final_url}")

                lower_body = body.lower()
                if any(marker in lower_body for marker in BLOCK_MARKERS):
                    print("RESULT: Possible CAPTCHA, access restriction, or bot check.")
                    failures += 1
                else:
                    matches = list(dict.fromkeys(PRICE_PATTERN.findall(body)))
                    if matches:
                        print(f"Price-like text found: {matches[:10]}")
                        print("RESULT: Price-like text is visible; extraction needs validation.")
                    else:
                        print("RESULT: Page opened, but no recognizable rupee price was found.")
                        failures += 1

                print(f"Page excerpt: {excerpt}")

            except Exception as exc:
                print(f"RESULT: Could not inspect page: {type(exc).__name__}: {exc}")
                failures += 1

        browser.close()

    print(f"\nDiagnostic finished. Products with issues: {failures}/{len(products)}")
    print("This is a connectivity diagnostic, not a verified price tracker.")


if __name__ == "__main__":
    main()
