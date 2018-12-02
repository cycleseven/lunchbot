from datetime import datetime

from lunchbot.events import SlackEvent


def test_should_return_correct_properties_for_new_message_events():
    slack_event = SlackEvent({
        "type": "message",
        "channel": "C2147483705",
        "user": "U2147483697",
        "text": "no",
        "ts": "1355517523.000005"
    })

    assert "1355517523.000005" == slack_event.get_ts()
    assert datetime.fromisoformat("2012-12-14T20:38:43") == slack_event.get_ts_as_datetime()
    assert "no" == slack_event.get_text()
    assert "U2147483697" == slack_event.get_user()
    assert "C2147483705" == slack_event.get_channel()


def test_should_return_correct_properties_for_edited_message_events():
    """For message_changed event, return the original `ts` value, *not* the new one."""
    slack_event = SlackEvent({
        "type": "message",
        "subtype": "message_changed",
        "hidden": True,
        "channel": "C2147483705",
        "ts": "1358878755.000001",
        "message": {
            "type": "message",
            "user": "U2147483697",
            "text": "yes",
            "ts": "1355517523.000005",
            "edited": {
                "user": "U2147483697",
                "ts": "1358878755.000001"
            }
        }
    })

    # Note that the returned ts refers to the *original* message, not the time
    # of the edit!
    assert "1355517523.000005" == slack_event.get_ts()
    assert datetime.fromisoformat("2012-12-14T20:38:43") == slack_event.get_ts_as_datetime()
    assert "yes" == slack_event.get_text()
    assert "U2147483697" == slack_event.get_user()
    assert "C2147483705" == slack_event.get_channel()


def test_should_recognise_message_events_vs_other_events():
    non_message_event = SlackEvent({"type": "not_a_message"})
    assert not non_message_event.is_valid_message()

    message_event = SlackEvent({"type": "message"})
    assert message_event.is_valid_message()
