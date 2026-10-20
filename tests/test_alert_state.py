
# File: tests/test_alert_state.py
from src.alert_state import should_alert, mark_alert_sent


def test_alert_can_be_sent_once():
    state = {}

    assert should_alert(state, "p1", "target", 100)

    mark_alert_sent(state, "p1", "target", 100)

    assert not should_alert(state, "p1", "target", 99)


def test_alert_rearms_after_price_rises_above_reset():
    state = {}

    mark_alert_sent(state, "p1", "target", 100)

    # Rising above the reset threshold re-arms the alert,
    # but must not trigger an alert on that same run.
    assert not should_alert(
        state, "p1", "target", 110, reset_price=105
    )

    # Once re-armed, the next run can trigger an alert.
    assert should_alert(
        state, "p1", "target", 106, reset_price=105
    )


def test_alert_types_are_tracked_separately():
    state = {}

    mark_alert_sent(state, "p1", "target", 100)

    assert should_alert(state, "p1", "low_price", 90)
    assert not should_alert(state, "p1", "target", 90)


def test_invalid_price_does_not_trigger_alert():
    state = {}

    assert not should_alert(state, "p1", "target", None)
    assert not should_alert(state, "p1", "target", 0)
