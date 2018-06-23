from lunchbot_message import LunchbotMessage


def test_should_recognise_yes_no_from_new_message_events():
    no_message = LunchbotMessage({
        "type": "message",
        "channel": "C2147483705",
        "user": "U2147483697",
        "ts": "1355517523.000005",

        # Text is no, so a YN_NO_RESPONSE is expected
        "text": "no"
    })
    assert no_message.get_yn_response() == LunchbotMessage.YN_NO_RESPONSE

    yes_message = LunchbotMessage({
        "type": "message",
        "channel": "C2147483705",
        "user": "U2147483697",
        "ts": "1355517523.000005",

        # Text is yes, so a YN_YES_RESPONSE is expected
        "text": "yes"
    })
    assert yes_message.get_yn_response() == LunchbotMessage.YN_YES_RESPONSE

    neutral_message = LunchbotMessage({
        "type": "message",
        "channel": "C2147483705",
        "user": "U2147483697",
        "ts": "1355517523.000005",

        # Text contains neither yes or no, so a YN_RESPONSE_NOT_FOUND is expected
        "text": "I'm talking about something totally unrelated."
    })
    assert neutral_message.get_yn_response() == LunchbotMessage.YN_RESPONSE_NOT_FOUND


def test_should_recognise_yes_no_from_edit_message_events():
    yes_message = LunchbotMessage({
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
    assert yes_message.get_yn_response() == LunchbotMessage.YN_YES_RESPONSE
