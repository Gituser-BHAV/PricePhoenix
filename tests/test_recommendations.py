from src.recommendation_engine import recommend

def test_target_reached_means_buy_now():
    result = recommend(2500, 2500)
    assert result["label"] == "BUY NOW"

def test_above_target_without_history_means_wait():
    result = recommend(2600, 2500, [])
    assert result["label"] == "WAIT"

def test_good_deal_requires_enough_history():
    settings = {"minimum_history_points_for_trend": 5, "good_deal_discount_percent": 15}
    result = recommend(2500, 2000, [3200, 3100, 3000, 2900, 2800], settings)
    assert result["label"] == "GOOD DEAL"

def test_missing_price_is_no_data():
    assert recommend(None, 2500)["label"] == "NO DATA"
