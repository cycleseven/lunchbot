from lunchbot.events import LunchbotMessageEvent


def test_should_recognise_yes_no_from_new_message_events():
    no_message = LunchbotMessageEvent({
        "type": "message",
        "channel": "C2147483705",
        "user": "U2147483697",
        "ts": "1355517523.000005",

        # Text is no, so user didn't bring lunch
        "text": "no"
    })
    assert no_message.did_user_bring_lunch() is False

    yes_message = LunchbotMessageEvent({
        "type": "message",
        "channel": "C2147483705",
        "user": "U2147483697",
        "ts": "1355517523.000005",

        # Text is yes, so user *did* bring lunch
        "text": "yes"
    })
    assert yes_message.did_user_bring_lunch() is True

    neutral_message = LunchbotMessageEvent({
        "type": "message",
        "channel": "C2147483705",
        "user": "U2147483697",
        "ts": "1355517523.000005",

        # Text contains neither yes or no, so this is a neutral message
        "text": "I'm talking about something totally unrelated."
    })

    # did_user_bring_lunch() returns None for neutral messages
    assert neutral_message.did_user_bring_lunch() is None


def test_should_recognise_yes_no_from_edit_message_events():
    yes_message = LunchbotMessageEvent({
        "type": "message",
        "subtype": "message_changed",
        "hidden": True,
        "channel": "C2147483705",
        "ts": "1358878755.000001",
        "message": {
            "type": "message",
            "user": "U2147483697",

            # Text is yes, so user *did* bring lunch
            "text": "yes",
            "ts": "1355517523.000005",
            "edited": {
                "user": "U2147483697",
                "ts": "1358878755.000001"
            }
        }
    })
    assert yes_message.did_user_bring_lunch() is True
