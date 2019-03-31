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


def get_words_of_encouragement(ratio):
    """Return an English sentence summarising how good the ratio is"""

    if 0 <= ratio <= 0.2:
        return random.choice([
            "there is nowhere to go but up",
            "that is not that good sorry",
            "clean your room",
            "there is always next month",
            "lol",
            "to be honest katsu curry is really nice so fair play",
            "could not be worse",
            "nah fam",
            "peak",
            "problematic",
        ])
    elif 0.2 < ratio <= 0.4:
        return random.choice([
            "it is an ok ratio i think but i think you can do even better next time but well done though",
            "cool",
            "not bad",
            "if you don't like having money then this is a pretty good ratio",
            "with more dedication i'm sure you can do better next time but well done",
            "hm",
            "ok",
            "i am feeling lukewarm about this score",
            "could be worse"
        ])
    elif 0.4 < ratio <= 0.6:
        return random.choice([
            "it is a good ratio well done",
            "not bad at all",
            "it is a nice one",
            "this is very respectable congratulations",
            "you are good",
            "yes",
            "merely hench"
        ])
    elif 0.6 < ratio <= 0.8:
        return random.choice([
            "that really is great",
            "gawn yersel",
            "that is a fantastic ratio, enjoy your money",
            "this is how you do it everyone",
            "WOAH!!! good one",
            "a picture of excellence",
            "perfect 5/7"
        ])
    elif 0.8 < ratio <= 1:
        return random.choice([
            "a tremendous display of dedication to the art of preparation",
            "a true hero",
            "wow that is an inspiring ratio",
            "well well well !!! look at what we have here, that is really incredible. well done",
            "i never thought i would see this in my lifetime wow",
            "now you are just showing off",
        ])
    else:
        raise ValueError(f"Unhandled ratio {ratio}")


def get_concrete_example_of_the_value_of_saving(estimated_money_saved):
    # Either give the estimated money saved as a % of a huge goal, or
    # say how many small things could be purchased
    if random.choice([True, False]):
        # The expensive goals are in this branch
        goal = random.choice([
            {"name": "a housing deposit in london", "value_gbp": 80000},
            {"name": "a Tesla Model S™", "value_gbp": 73500},
            {"name": "an average second-hand yacht", "value_gbp": 6528984},
            {
                "name": "a small loan of a million dollars for your children (according to exchange rate at time of writing)",
                "value_gbp": 777200
            },
        ])

        percentage_of_goal_achieved = (estimated_money_saved / goal["value_gbp"]) * 100
        return f"{percentage_of_goal_achieved}% of {goal['name']}"
    else:
        # The cheap goals are in this branch
        goal = random.choice([
            {"name": "bananas from a convenience supermarket", "value_gbp": 0.25},
            {"name": "bananas from a big supermarket", "value_gbp": 0.13},
            {"name": "items of your choice from a pound shop", "value_gbp": 1},
            {"name": "plastic coat hangers", "value_gbp": 0.26},
            {"name": "balls of 200 multicolored rubber bands", "value_gbp": 5},
        ])

        number_of_goals_achieved = estimated_money_saved / goal["value_gbp"]
        return f"{number_of_goals_achieved} {goal['name']}"


def summarise_stat(stat):
    """Return an English paragraph summarising the monthly stat for a user"""

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

    return (
        f'{stat["name"]} my {random.choice(pet_names)}\n'
        f'{stat["good_days"]}/{stat["total_days"]}\n'
        f'{get_words_of_encouragement(ratio)}\n'
        f'you have saved an estimated £{stat["estimated_money_saved"]} this month\n'
        f'with that money you could buy {get_concrete_example_of_the_value_of_saving(stat["estimated_money_saved"])}'
    )


def summarise_winners(winners):
    if len(winners) == 1:
        return f"our winner for the month is\n:tada: {winners[0]} :tada:"
    else:
        return f"our winners for the month are\n:tada: {' and '.join(winners)} :tada:"


def summarise_results(stats):
    """Return the text for the monthly report"""

    stat_summaries = "\n\n".join([summarise_stat(stat) for stat in stats])
    winners = get_winners(stats)
    greeting = random.choice([
        "well what a month it has been",
        "yes that's right it is that time again",
        "let's do this",
        "here we go once more"
    ])
    signoff = random.choice([
        "i will be listening from the shadows",
        "i am always watching",
        "bye",
        "until next time"
    ])

    return (
        f"hello it is lunchbot here with the monthly summary\n\n"
        f"{greeting}\n\n"
        f"{stat_summaries}\n\n"
        f"that means....... that is correct\n"
        f"you know it\n"
        f"{summarise_winners(winners)}\n\n"
        f"congratulations and speak to you all next month\n"
        f"{signoff}"
    )
