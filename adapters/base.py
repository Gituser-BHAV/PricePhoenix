class PriceSourceError(RuntimeError):
    pass

def fetch_product(product):
    """Return {name, price, currency, in_stock, product_url} or raise PriceSourceError."""
    raise NotImplementedError
