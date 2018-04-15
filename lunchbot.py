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


def is_subsequence(short_list, long_list):
    """
    Return true if short_list is a subsequence of long_list.
    """
    if len(short_list) > len(long_list):
        return False

    for i, _ in enumerate(long_list):
        looks_good = True

        for j, a_item in enumerate(short_list):
            if a_item != long_list[i + j]:
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
        # Completely randomized choice
        return "thumbsup"
    else:
        return "thumbsdown"


def react_with_emoji(channel_id, timestamp, did_bring_lunch):
    """
    If did_bring_lunch is true, react with a positive emoji. Otherwise react with a negative emoji (eg. thumbs down).
    """
    return sc.api_call(
        "reactions.add",
        channel=channel_id,
        name=get_random_emoji(did_bring_lunch),
        timestamp=timestamp
    )


def handle_yes_no_response(message_event, did_bring_lunch):
    """
    Store a yes/no boolean response in Dynamo.
    """
    timestamp = message_event["ts"]
    print("Recorded timestamp")
    print(datetime.utcfromtimestamp(float(timestamp)))

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
                "S": message_event["user"],
            },
            "did_bring_lunch": {
                "BOOL": did_bring_lunch
            },
        }
    )
    print(dynamo_response)
    react_with_emoji(message_event["channel"], message_event["ts"], did_bring_lunch)


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


def detect_yes_no_response(message_event):
    """
    Detect messages that indicate a "yes" or "no" response from a user.
    """
    tokens = message_event["text"].lower().split()

    if "yes" in tokens or is_subsequence(["y", "e", "s"], tokens):
        print("Affirmative response detected using complex deep neural net algorithm.")
        invalidate_previous_responses_from_today(message_event)
        handle_yes_no_response(message_event, did_bring_lunch=True)
    elif "no" in tokens or is_subsequence(["n", "o"], tokens):
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
