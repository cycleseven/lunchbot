from datetime import datetime
from pprint import pformat

from lunchbot import logging
from lunchbot.services import Slack


logger = logging.getLogger(__name__)


def count_good_days(records):
    """A "good" day is a day when the user brought lunch"""
    return sum(1 for record in records if record["did_bring_lunch"])


def estimate_money_saved(records):
    """The average £££ saved by bringing your own lunch would ideally be configurable to suit different teams :)
    To keep things simple, a value is hardcoded here."""
    average_lunch_saving_in_pounds = 4
    num_good_days = count_good_days(records)
    return average_lunch_saving_in_pounds * num_good_days


def get_distinct_users(records):
    return set(record["user_id"] for record in records)


def fetch_users(records):
    """Query the Slack API for the names of all unique users in the records. Return
    each user as a dict of { "id", "name" }"""
    distinct_user_ids = get_distinct_users(records)

    users = []
    for user_id in distinct_user_ids:
        slack_client = Slack.get_client()
        slack_response = slack_client.api_call("users.info", user=user_id)

        logger.debug(f"Checked user name for user ID {user_id}")
        logger.debug(pformat(slack_response))

        if slack_response["ok"]:
            users.append({
                "id": user_id,
                "name": slack_response["user"]["name"]
            })

    return users


def count_distinct_days(records):
    return len(set(
        datetime.utcfromtimestamp(record["timestamp"]).date()
        for record in records
    ))
