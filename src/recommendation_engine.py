def recommend(current_price, target_price, history_prices=None, settings=None):
    """Return a transparent recommendation object; never claims to predict future prices."""
    history_prices = history_prices or []
    settings = settings or {}
    if current_price is None or current_price <= 0:
        return {"label": "NO DATA", "reason": "No valid current price is available."}

    if current_price <= target_price:
        return {
            "label": "BUY NOW",
            "reason": "The current price is at or below your target price."
        }

    min_points = int(settings.get("minimum_history_points_for_trend", 5))
    good_deal_discount = float(settings.get("good_deal_discount_percent", 15))

    if len(history_prices) >= min_points:
        average = sum(history_prices) / len(history_prices)
        if average > 0:
            discount_from_average = (average - current_price) / average * 100
            if discount_from_average >= good_deal_discount:
                return {
                    "label": "GOOD DEAL",
                    "reason": (
                        f"Current price is {discount_from_average:.1f}% below the "
                        f"average of recorded observations; it is still above your target."
                    )
                }
            if len(history_prices) >= 2 and history_prices[-1] < history_prices[0]:
                return {
                    "label": "WAIT",
                    "reason": "The recent recorded prices are trending downward, and the target has not been reached."
                }

    return {
        "label": "WAIT",
        "reason": "The target has not been reached and there is not enough evidence for a stronger recommendation."
    }
