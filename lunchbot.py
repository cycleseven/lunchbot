import random
from decimal import Decimal

import boto3
import json
import os
import uuid
from datetime import datetime, timedelta

from boto3.dynamodb.conditions import Key

from slackclient import SlackClient

slack_token = os.environ["SLACK_API_TOKEN"]
sc = SlackClient(slack_token)
dynamodb = boto3.client("dynamodb")


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


def is_subsequence(short_list, long_list):
    """
    Return true if short_list is a subsequence of long_list.
    """
    print("is_subseq")
    print(short_list)
    print(long_list)

    if len(short_list) > len(long_list):
        return False

    for i, _ in enumerate(long_list):
        looks_good = True

        for j, item_from_short_list in enumerate(short_list):
            if len(long_list) - j == 0:
                break

            if item_from_short_list != long_list[i + j]:
                looks_good = False
                break

        if looks_good:
            return True

    return False


def get_random_emoji(is_positive):
    """
    Pick a random positive or negative emoji based on is_positive flag.
    """
    if is_positive:
        return random.choice(positive_emojis)
    else:
        return random.choice(negative_emojis)


def handle_yes_no_response(message_event, did_bring_lunch):
    """
    Store a yes/no boolean response in Dynamo.
    """
    timestamp = message_event["ts"]
    print("Recorded timestamp")
    print(datetime.utcfromtimestamp(float(timestamp)))

    emoji = get_random_emoji(did_bring_lunch)
    print("adding emoji")
    print(emoji)
    slack_response = sc.api_call(
        "reactions.add",
        channel=message_event["channel"],
        name=emoji,
        timestamp=timestamp
    )
    print(slack_response)

    dynamo_response = dynamodb.put_item(
        TableName=os.environ["DYNAMODB_TABLE"],
        Item={
            "id": {
                "S": str(uuid.uuid4())
            },
            "timestamp": {
                "N": timestamp
            },
            "user_id": {
                "S": message_event["user"]
            },
            "channel_id": {
                "S": message_event["channel"]
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


def invalidate_previous_responses_from_today(message_event):
    """
    Query for existing responses and delete them.
    :param message_event:
    :return:
    """
    now = datetime.utcnow()
    start_of_today = datetime(now.year, now.month, now.day).timestamp()
    print("user_id")
    print(message_event["user"])

    dynamo_resource = boto3.resource("dynamodb")
    table = dynamo_resource.Table(os.environ["DYNAMODB_TABLE"])

    dynamo_response = table.query(
        ConsistentRead=True,
        KeyConditionExpression=Key("user_id").eq(message_event["user"]) & Key("timestamp").gte(Decimal(start_of_today))
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

    delete_response = dynamo_resource.batch_write_item(
        RequestItems={
            os.environ["DYNAMODB_TABLE"]: delete_requests
        }
    )
    print(delete_response)

    for item in dynamo_response["Items"]:
        response = sc.api_call(
            "reactions.remove",
            channel=message_event["channel"],
            name=item["emoji"],
            timestamp=item["timestamp"]
        )
        print("Slack remove emoji response")
        print(response)


def appears_in(word, tokens):
    """
    Return true if the word appears in the list of lexical tokens
    """
    return word in tokens or is_subsequence(list(word), tokens)


def detect_yes_no_response(message_event):
    """
    Detect messages that indicate a "yes" or "no" response from a user.
    """
    tokens = message_event["text"].lower().split()

    positive_words = [
        "yes",
        "aye",
        "yeah"
    ]

    negative_words = [
        "no",
        "cilia"
    ]

    if any(appears_in(word, tokens) for word in positive_words):
        print("Affirmative response detected using complex deep neural net algorithm.")
        invalidate_previous_responses_from_today(message_event)
        handle_yes_no_response(message_event, did_bring_lunch=True)
    elif any(appears_in(word, tokens) for word in negative_words):
        print("Negative response detected using complex deep neural net algorithm.")
        invalidate_previous_responses_from_today(message_event)
        handle_yes_no_response(message_event, did_bring_lunch=False)


def on_slack_event(event, context):
    """
    Lambda handler called when a new event from Slack is POSTed.
    """
    try:
        body = json.loads(event["body"])
        message_event = body["event"]
        print(body)
    except KeyError:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Malformed event in request body."
            })
        }

    if message_event["type"] != "message":
        return {
            "statusCode": 200,
            "body": "Ignoring non-message event."
        }

    detect_yes_no_response(message_event)

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Successfully processed Slack event."})
    }
