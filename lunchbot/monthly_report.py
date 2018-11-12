from lunchbot.services import Slack


def count_good_days(records):
    """A "good" day is a day when the user brought lunch"""
    return sum(1 for record in records if record["did_bring_lunch"])


def estimate_money_saved(records):
    """The average lunch cost would ideally be configurable to suit different teams. To keep things simple,
    £5 is hardcoded here."""
    average_lunch_cost_in_pounds = 5
    num_good_days = count_good_days(records)
    return average_lunch_cost_in_pounds * num_good_days


def get_distinct_users(records):
    return set(record["user_id"] for record in records)


def fetch_user_name(user_id):
    slack_client = Slack.get_client()
    slack_response = slack_client.api_call("users.profile.get", user=user_id)
    return slack_response["profile"]["name"]