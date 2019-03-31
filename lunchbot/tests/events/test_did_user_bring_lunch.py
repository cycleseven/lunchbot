from lunchbot.events import LunchbotMessageEvent


def test_should_recognise_yes_no_from_new_message_events():
    no_message = LunchbotMessageEvent({"type": "message", "text": "no"})
    assert no_message.did_user_bring_lunch() is False

    yes_message = LunchbotMessageEvent({"type": "message", "text": "yes"})
    assert yes_message.did_user_bring_lunch() is True

    neutral_message = LunchbotMessageEvent(
        {"type": "message", "text": "I'm talking about something totally unrelated."}
    )

    # did_user_bring_lunch() returns None for neutral messages
    assert neutral_message.did_user_bring_lunch() is None


def test_should_recognise_yes_no_from_edit_message_events():
    yes_message = LunchbotMessageEvent(
        {
            "type": "message",
            "subtype": "message_changed",
            "message": {"type": "message", "text": "yes"},
        }
    )
    assert yes_message.did_user_bring_lunch() is True


def test_should_handle_spaces_between_characters():
    yes_message = LunchbotMessageEvent({"type": "message", "text": "y   e   s"})
    assert yes_message.did_user_bring_lunch() is True


def test_should_handle_surrounding_content():
    yes_message = LunchbotMessageEvent(
        {"type": "message", "text": "yes I did bring lunch"}
    )
    assert yes_message.did_user_bring_lunch() is True


def test_should_handle_capitalisation_differences():
    yes_message = LunchbotMessageEvent({"type": "message", "text": "Yes"})
    assert yes_message.did_user_bring_lunch() is True

    no_message = LunchbotMessageEvent({"type": "message", "text": "nO"})
    assert no_message.did_user_bring_lunch() is False
