from lunchbot import detect_yes_no_response, YN_YES_RESPONSE, YN_NO_RESPONSE


def test_should_recognise_yes_no_from_new_message_events():
    message_event = {
        "type": "message",
        "channel": "C2147483705",
        "user": "U2147483697",
        "text": "no",
        "ts": "1355517523.000005"
    }
    yn_response = detect_yes_no_response(message_event)
    assert yn_response == YN_NO_RESPONSE


def test_should_recognise_yes_no_from_edit_message_events():
    message_event = {
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
    yn_response = detect_yes_no_response(message_event)
    assert yn_response == YN_YES_RESPONSE
