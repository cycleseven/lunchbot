import random
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


def get_monthly_stats(records, users):
    stats = []
    for user in users:
        user_records = [record for record in records if record["user_id"] == user["id"]]
        stats.append({
            "name": user["name"],
            "good_days": count_good_days(user_records),
            "total_days": count_distinct_days(records),
            "estimated_money_saved": estimate_money_saved(user_records),
        })

    return stats


def get_winners(stats):
    max_good_days = max(stats, key=lambda item: item["good_days"])["good_days"]
    return [stat["name"] for stat in stats if stat["good_days"] == max_good_days]


def summarise_stat(stat):
    pet_names = [
        "sweet pea",
        "human",
        "fellow",
        "angel",
        "colleague",
        "boiii",
        "friend",
        "individual",
        "person",
        "muffin",
        "amiga/amigo",
        "inspiration",
        "acquaintance"
    ]

    ratio = stat["good_days"] / stat["total_days"]

    if 0 <= ratio <= 0.2:
        words_of_encouragement = random.choice([
            "there is nowhere to go but up",
            "that is not that good sorry",
            "clean your room",
            "there is always next month",
            "lol",
            "to be honest katsu curry is really nice so fair play",
        ])
    elif 0.2 < ratio <= 0.4:
        words_of_encouragement = random.choice([
            "it is an ok ratio i think but i think you can do even better next time but well done though",
            "cool",
            "not bad",
            "if you don't like having money then this is a pretty good ratio",
            "with more dedication i'm sure you can do better next time but well done",
            "hm"
        ])
    elif 0.4 < ratio <= 0.6:
        words_of_encouragement = random.choice([
            "it is a good ratio well done",
            "not bad at all",
            "it is a nice one",
            "this is very respectable congratulations",
            "you are good",
            "yes",
        ])
    elif 0.6 < ratio <= 0.8:
        words_of_encouragement = random.choice([
            "that really is great",
            "gawn yersel",
            "that is a fantastic ratio, enjoy your money",
            "this is how you do it everyone",
            "WOAH!!! good one",
            "a picture of excellence",
            "perfect 5/7"
        ])
    elif 0.8 < ratio <= 1:
        words_of_encouragement = random.choice([
            "a tremendous display of dedication to the art of preparation",
            "a true hero",
            "wow that is an inspiring ratio",
            "well well well !!! look at what we have here, that is really incredible. well done",
            "i never thought i would see this in my lifetime wow",
            "now you are just showing off",
        ])
    else:
        raise ValueError(f"Unhandled ratio {ratio}")

    return (
        f'{stat["name"]} my {random.choice(pet_names)}\n'
        f'{stat["good_days"]}/{stat["total_days"]}\n'
        f'{words_of_encouragement}\n'
        f'you have saved an estimated £{stat["estimated_money_saved"]} this month\n'
    )


def summarise_winners(winners):
    if len(winners) == 1:
        return f"our winner for the month is\n:tada: {winners[0]} :tada:"
    else:
        return f"our winners for the month are\n:tada: {' and '.join(winners)} :tada:"


def summarise_results(stats):
    stat_summaries = "\n".join([summarise_stat(stat) for stat in stats])
    winners = get_winners(stats)

    return (
        f"hello it is lunchbot here with the monthly summary\n\n"
        f"well what a month it has been\n\n"
        f"{stat_summaries}\n"
        f"that means....... that is correct\n"
        f"you know it\n"
        f"{summarise_winners(winners)}\n"
        f"congratulations and speak to you all next month\n"
        f"{random.choice(['i will be listening from the shadows', 'i am always watching'])}"
    )
