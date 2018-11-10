import json

from lunchbot.strings import appears_in


class SlackEvent(object):
    """Represents an event from the Slack API."""

    def __init__(self, raw_event):
        self._raw_event = raw_event

    def is_valid_message(self):
        return self._raw_event["type"] == "message"

    def get_channel(self):
        return self._raw_event["channel"]

    def get_ts(self):
        """Return the ts (Slack timestamp/ID) for the message.

        In the case of messaged_changed events, the original ts of the old message is returned instead of the new ts.
        """
        return self._get_message()["ts"]

    def get_text(self):
        return self._get_message()["text"]

    def get_user(self):
        return self._get_message()["user"]

    def _get_message(self):
        if "subtype" in self._raw_event and self._raw_event["subtype"] == "message_changed":
            return self._raw_event["message"]
        else:
            return self._raw_event


class LunchbotMessageEvent(SlackEvent):
    YN_YES_RESPONSE = "YN_YES_RESPONSE"
    YN_NO_RESPONSE = "YN_NO_RESPONSE"
    YN_RESPONSE_NOT_FOUND = "YN_RESPONSE_NOT_FOUND"

    positive_words = [
        "yes",
        "aye",
        "yeah"
    ]

    negative_words = [
        "no",
        "cilia"
    ]

    @staticmethod
    def create_from_api_gateway_event(event):
        body = json.loads(event["body"])
        return LunchbotMessageEvent(body["event"])

    def get_yn_response(self):
        """Return YN_YES_RESPONSE if a "yes" is detected in the message, or YN_NO_RESPONSE for no. Otherwise, return
        YN_RESPONSE_NOT_FOUND.
        """
        text = self.get_text()
        tokens = text.lower().split()

        if any(appears_in(word, tokens) for word in self.positive_words):
            print("Affirmative response detected using complex deep neural net algorithm.")
            return self.YN_YES_RESPONSE
        elif any(appears_in(word, tokens) for word in self.negative_words):
            print("Negative response detected using complex deep neural net algorithm.")
            return self.YN_NO_RESPONSE
        else:
            return self.YN_RESPONSE_NOT_FOUND
