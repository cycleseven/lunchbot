import random

from lunchbot_records import get_todays_records_for_user, delete_records, store_record

positive_emojis = [
    "thumbsup",
    "heart_eyes",
    "heart_eyes_cat",
    "grinning_face_with_star_eyes",
    "ok_hand",
    "muscle",
    "100",
    "sunglasses",
    "money_mouth_face",
    "chart",
    "moneybag",
    "kissing_heart",
    "angel",
    "dancer",
    "man_dancing",
    "the_horns",
    "call_me_hand",
    "fist",
    "i_love_you_hand_sign",
    "raised_hands",
    "handshake",
    "clap",
    "heart",
    "tada",
    "sparkles",
    "medal",
    "star",
    "rainbow",
    "fire",
    "white_check_mark",
    "heavy_check_mark",
]

negative_emojis = [
    "money_with_wings",
    "persevere",
    "sweat",
    "sob",
    "scream",
    "face_with_head_bandage",
    "skull",
    "poop",
    "see_no_evil",
    "scream_cat",
    "man-gesturing-no",
    "woman-gesturing-no",
    "man-shrugging",
    "woman-shrugging",
    "man-facepalming",
    "woman-facepalming",
    "facepunch",
    "third_place_medal",
    "moyai",
    "no_entry",
    "no_entry_sign",
    "heavy_multiplication_x",
    "x",
    "negative_squared_cross_mark",
]


def get_random_emoji(is_positive):
    """
    Pick a random positive or negative emoji based on is_positive flag.
    """
    if is_positive:
        return random.choice(positive_emojis)
    else:
        return random.choice(negative_emojis)


def handle_yes_no_response(lunchbot_message, did_bring_lunch, sc):
    emoji = get_random_emoji(did_bring_lunch)
    print("adding emoji")
    print(emoji)
    slack_response = sc.api_call(
        "reactions.add",
        channel=lunchbot_message.get_channel(),
        name=emoji,
        timestamp=lunchbot_message.get_ts()
    )
    print(slack_response)

    store_record(
        ts=lunchbot_message.get_ts(),
        user_id=lunchbot_message.get_user(),
        channel_id=lunchbot_message.get_channel(),
        did_bring_lunch=did_bring_lunch,
        emoji=emoji
    )


def invalidate_previous_responses_from_today(sc, lunchbot_message):
    """Query for existing responses and delete them."""
    todays_records_for_user = get_todays_records_for_user(lunchbot_message.get_user())

    if len(todays_records_for_user) == 0:
        return

    # Remove old Slack emoji reactions
    for record in todays_records_for_user:
        response = sc.api_call(
            "reactions.remove",
            channel=lunchbot_message.get_channel(),
            name=record["emoji"],
            timestamp=record["slack_ts"]
        )
        print("Slack remove emoji response")
        print(response)

    delete_records(todays_records_for_user)
