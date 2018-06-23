from slack_event import SlackEvent

# Sample events
normal_message_raw_event = {
    "type": "message",
    "channel": "C2147483705",
    "user": "U2147483697",
    "text": "no",
    "ts": "1355517523.000005"
}

message_changed_raw_event = {
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
}


def test_should_return_correct_properties_for_normal_messages():
    slack_event = SlackEvent(normal_message_raw_event)
    assert slack_event.get_ts() == "1355517523.000005"


def test_should_return_original_ts_for_message_changed_subtype():
    """For message_changed event, return the original `ts` value, *not* the new one."""
    slack_event = SlackEvent(message_changed_raw_event)
    assert slack_event.get_ts() == "1355517523.000005"


def test_should_return_text_for_normal_messages():
    slack_event = SlackEvent(normal_message_raw_event)
    assert slack_event.get_text() == "no"


def test_should_return_text_for_message_changed_subtype():
    """For message_changed event, return the original `ts` value, *not* the new one."""
    slack_event = SlackEvent(message_changed_raw_event)
    assert slack_event.get_text() == "yes"


def test_should_return_user_for_normal_messages():
    slack_event = SlackEvent(normal_message_raw_event)
    assert slack_event.get_user() == "U2147483697"


def test_should_return_user_for_message_changed_subtype():
    slack_event = SlackEvent(message_changed_raw_event)
    assert slack_event.get_user() == "U2147483697"


def test_should_return_channel_for_normal_messages():
    slack_event = SlackEvent(normal_message_raw_event)
    assert slack_event.get_channel() == "C2147483705"


def test_should_return_channel_for_message_changed_subtype():
    slack_event = SlackEvent(message_changed_raw_event)
    assert slack_event.get_channel() == "C2147483705"


def test_should_recognise_message_events_vs_other_events():
    non_message_event = SlackEvent({"type": "not_a_message"})
    assert not non_message_event.is_message()

    message_event = SlackEvent(normal_message_raw_event)
    assert message_event.is_message()


def test_should_recognise_yes_no_from_new_message_events():
    yes_event = SlackEvent({
        "type": "message",
        "channel": "C2147483705",
        "user": "U2147483697",
        "ts": "1355517523.000005",

        # Text is no, so a YN_NO_RESPONSE is expected
        "text": "no"
    })
    assert yes_event.get_yn_response() == SlackEvent.YN_NO_RESPONSE

    yes_event = SlackEvent({
        "type": "message",
        "channel": "C2147483705",
        "user": "U2147483697",
        "ts": "1355517523.000005",

        # Text is yes, so a YN_YES_RESPONSE is expected
        "text": "yes"
    })
    assert yes_event.get_yn_response() == SlackEvent.YN_YES_RESPONSE

    neutral_event = SlackEvent({
        "type": "message",
        "channel": "C2147483705",
        "user": "U2147483697",
        "ts": "1355517523.000005",

        # Text contains neither yes or no, so a YN_RESPONSE_NOT_FOUND is expected
        "text": "I'm talking about something totally unrelated."
    })
    assert neutral_event.get_yn_response() == SlackEvent.YN_RESPONSE_NOT_FOUND


def test_should_recognise_yes_no_from_edit_message_events():
    yes_event = SlackEvent({
        "type": "message",
        "subtype": "message_changed",
        "hidden": True,
        "channel": "C2147483705",
        "ts": "1358878755.000001",
        "message": {
            "type": "message",
            "user": "U2147483697",

            # Text is yes, so a YN_YES_RESPONSE is expected
            "text": "yes",
            "ts": "1355517523.000005",
            "edited": {
                "user": "U2147483697",
                "ts": "1358878755.000001"
            }
        }
    })
    assert yes_event.get_yn_response() == SlackEvent.YN_YES_RESPONSE
