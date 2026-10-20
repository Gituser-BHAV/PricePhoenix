from adapters.base import PriceSourceError

def fetch_product(product):
    # Intentionally not scraping Flipkart pages. Implement only after configuring
    # an official or otherwise permitted data source and credentials.
    raise PriceSourceError(
        "Flipkart adapter is not configured. Use source='mock' for tests, or "
        "implement an authorized API data source for which you have access."
    )
