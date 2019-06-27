from datetime import datetime
import json
import logging

from lunchbot.calendar import get_last_friday_of_month
from lunchbot.strings import appears_in


logger = logging.getLogger(__name__)


class SlackEvent(object):
    """Represents an event from the Slack API."""

    def __init__(self, raw_event):
        self._raw_event = raw_event

    def is_valid_message(self):
        """The API only handles newly created + edited messages."""
        return self._raw_event["type"] == "message" and self._get_subtype() in [
            None,
            "message_changed",
        ]

    def get_channel(self):
        return self._raw_event["channel"]

    def get_ts(self):
        """Return the ts (Slack timestamp/ID) for the message.

        In the case of messaged_changed events, the original ts of the old message is returned
        instead of the new ts.
        """
        return self._get_message()["ts"]

    def get_ts_as_datetime(self):
        """Return the parsed timestamp as a Python datetime object."""
        return datetime.utcfromtimestamp(int(float(self.get_ts())))

    def get_text(self):
        return self._get_message()["text"]

    def get_user(self):
        return self._get_message()["user"]

    def _get_message(self):
        if self._get_subtype() == "message_changed":
            return self._raw_event["message"]
        else:
            return self._raw_event

    def _get_subtype(self):
        """Return the subtype of the message event.

        Possible return values:
            None               - a real user posted a new message.
            "message_changed"  - an edit was made to an existing message.
            "bot_message"      - a bot posted a new message.
            "message_deleted"  - an existing message was deleted.
        """
        return self._raw_event.get("subtype")


class LunchbotMessageEvent(SlackEvent):
    positive_words = ["yes", "aye", "yeah", "yep"]

    negative_words = ["no", "nope", "not"]

    @staticmethod
    def create_from_api_gateway_event(api_gateway_event):
        http_body = json.loads(api_gateway_event["body"])
        return LunchbotMessageEvent(http_body["event"])

    def did_user_bring_lunch(self):
        """Return True if a "yes" is detected in the message, or False for no. Otherwise, return
        None.
        """
        text = self.get_text()
        tokens = text.lower().split()

        if any(appears_in(word, tokens) for word in self.positive_words):
            logger.info(
                "Affirmative response detected using complex deep neural net algorithm."
            )
            return True
        elif any(appears_in(word, tokens) for word in self.negative_words):
            logger.info(
                "Negative response detected using complex deep neural net algorithm."
            )
            return False

    def get_working_month(self):
        """Return the working month for the event.

        The working month runs from one payday to the next (the last Friday of the month).

        Note that the working month might be different from the calendar month. Any working days
        following the last Friday of the month will actually be assigned to the *following* calendar
        month.
        """
        event_date = self.get_ts_as_datetime()
        last_friday_of_month = get_last_friday_of_month(
            event_date.year, event_date.month
        )

        # Events that happen after payday should be assigned to the following month
        if event_date.day > last_friday_of_month:
            next_month = event_date.month + 1

            # Loop around to the first month of next year in case it's one of the final
            # days of December
            if next_month == 13:
                return f"1/{event_date.year + 1}"
            else:
                return f"{next_month}/{event_date.year}"

        return f"{event_date.month}/{event_date.year}"


class ScheduledTaskOptions(object):
    @staticmethod
    def create_from_cloudwatch_event(cloudwatch_event):
        return ScheduledTaskOptions(cloudwatch_event)

    def __init__(self, cloudwatch_event):
        self._cloudwatch_event = cloudwatch_event

    def is_dry_run(self):
        return self._cloudwatch_event.get("dry_run") is not False
