from pprint import pformat

from lunchbot import emojis, db, logging
from lunchbot.services import Slack


logger = logging.get_logger(__name__)


class Lunchbot(object):
    def __init__(self, message_event):
        self.message_event = message_event
        self.slack_client = Slack.get_client()

    def react_to_message(self):
        """Send an emoji reaction in response to the message."""
        did_bring_lunch = self.message_event.did_user_bring_lunch()

        # Ignore neutral messages
        if did_bring_lunch is None:
            return

        self.invalidate_previous_responses_from_today()

        emoji = emojis.get_random_emoji(did_bring_lunch)
        slack_response = self.slack_client.api_call(
            "reactions.add",
            channel=self.message_event.get_channel(),
            name=emoji,
            timestamp=self.message_event.get_ts(),
        )

        logger.debug("Called reactions.add in Slack API")
        logger.debug(pformat(slack_response))

        db.store_record(
            ts=self.message_event.get_ts(),
            user_id=self.message_event.get_user(),
            channel_id=self.message_event.get_channel(),
            did_bring_lunch=did_bring_lunch,
            emoji=emoji,
            working_month=self.message_event.get_working_month(),
        )

    def invalidate_previous_responses_from_today(self):
        """Query for existing responses and delete them."""
        todays_records_for_user = db.get_todays_records_for_user(
            self.message_event.get_user()
        )

        if len(todays_records_for_user) == 0:
            return

        # Remove old Slack emoji reactions
        for record in todays_records_for_user:
            response = self.slack_client.api_call(
                "reactions.remove",
                channel=self.message_event.get_channel(),
                name=record["emoji"],
                timestamp=record["slack_ts"],
            )

            logger.debug("Called reactions.remove in Slack API")
            logger.debug(pformat(response))

        db.delete_records(todays_records_for_user)
