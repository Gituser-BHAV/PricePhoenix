from src.alert_state import should_alert, mark_alert_sent

def test_alert_can_be_sent_once():
    state = {}
    assert should_alert(state, "p1", "target", 100)
    mark_alert_sent(state, "p1", "target", 100)
    assert not should_alert(state, "p1", "target", 99)

def test_alert_rearms_after_price_rises_above_reset():
    state = {}
    mark_alert_sent(state, "p1", "target", 100)
    assert not should_alert(state, "p1", "target", 110, reset_price=105)
    assert should_alert(state, "p1", "target", 106, reset_price=105)
