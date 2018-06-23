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
