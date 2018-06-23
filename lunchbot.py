import random

import boto3
import os
import uuid

from datetime import datetime
from decimal import Decimal
from boto3.dynamodb.conditions import Key

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


def handle_yes_no_response(slack_event, did_bring_lunch, dynamodb, sc):
    """
    Store a yes/no boolean response in Dynamo.
    """
    print("Recorded timestamp")
    print(datetime.utcfromtimestamp(float(slack_event.get_ts())))

    emoji = get_random_emoji(did_bring_lunch)
    print("adding emoji")
    print(emoji)
    slack_response = sc.api_call(
        "reactions.add",
        channel=slack_event.get_channel(),
        name=emoji,
        timestamp=slack_event.get_ts()
    )
    print(slack_response)

    dynamo_response = dynamodb.put_item(
        TableName=os.environ["DYNAMODB_TABLE"],
        Item={
            "id": {
                "S": str(uuid.uuid4())
            },
            "timestamp": {
                "N": slack_event.get_ts()
            },
            "slack_ts": {
                "S": slack_event.get_ts()
            },
            "user_id": {
                "S": slack_event.get_user()
            },
            "channel_id": {
                "S": slack_event.get_channel()
            },
            "did_bring_lunch": {
                "BOOL": did_bring_lunch
            },
            "emoji": {
                "S": emoji
            }
        }
    )
    print(dynamo_response)


def invalidate_previous_responses_from_today(sc, slack_event):
    """Query for existing responses and delete them."""
    now = datetime.utcnow()
    start_of_today = datetime(now.year, now.month, now.day).timestamp()

    # Should move outside no? Resource created on every lambda invocation
    dynamo_resource = boto3.resource("dynamodb")
    table = dynamo_resource.Table(os.environ["DYNAMODB_TABLE"])

    dynamo_response = table.query(
        ConsistentRead=True,
        KeyConditionExpression=Key("user_id").eq(slack_event.get_user()) & Key("timestamp").gte(Decimal(start_of_today))
    )

    if len(dynamo_response["Items"]) == 0:
        return

    delete_requests = [
        {
            "DeleteRequest": {
                "Key": {
                    "user_id": item["user_id"],
                    "timestamp": item["timestamp"]
                }
            }
        } for item in dynamo_response["Items"]
    ]
    print(dynamo_response)

    for item in dynamo_response["Items"]:
        response = sc.api_call(
            "reactions.remove",
            channel=slack_event.get_channel(),
            name=item["emoji"],
            timestamp=item["slack_ts"]
        )
        print("Slack remove emoji response")
        print(response)

    delete_response = dynamo_resource.batch_write_item(
        RequestItems={
            os.environ["DYNAMODB_TABLE"]: delete_requests
        }
    )
    print(delete_response)
