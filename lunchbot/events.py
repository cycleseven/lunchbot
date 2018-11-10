import json
import logging

from lunchbot.strings import appears_in


logger = logging.getLogger(__name__)


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
    def create_from_api_gateway_event(api_gateway_event):
        http_body = json.loads(api_gateway_event["body"])
        return LunchbotMessageEvent(http_body["event"])

    def user_did_bring_lunch(self):
        """Return True if a "yes" is detected in the message, or False for no. Otherwise, return None."""
        text = self.get_text()
        tokens = text.lower().split()

        if any(appears_in(word, tokens) for word in self.positive_words):
            logger.info("Affirmative response detected using complex deep neural net algorithm.")
            return True
        elif any(appears_in(word, tokens) for word in self.negative_words):
            logger.info("Negative response detected using complex deep neural net algorithm.")
            return False
