import json
import os
from pprint import pprint

import boto3
from lunchbot import invalidate_previous_responses_from_today, handle_yes_no_response
from lunchbot_message import LunchbotMessage
from slackclient import SlackClient

slack_token = os.environ["SLACK_API_TOKEN"]
sc = SlackClient(slack_token)
dynamodb = boto3.client("dynamodb")


def on_slack_event(event, context):
    """
    Lambda handler called when a new event from Slack is POSTed.
    """
    print("Received event from Slack.")
    pprint(event)

    # Parse raw Lambda event to model (slack_event instance)
    try:
        body = json.loads(event["body"])
        message_event = body["event"]
    except KeyError:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Malformed event in request body."
            })
        }

    lunchbot_message = LunchbotMessage(message_event)

    if not lunchbot_message.is_valid_message():
        return {
            "statusCode": 200,
            "body": "Ignoring non-message event."
        }

    yn_response = lunchbot_message.get_yn_response()

    if yn_response != LunchbotMessage.YN_RESPONSE_NOT_FOUND:
        invalidate_previous_responses_from_today(sc, lunchbot_message)

        if yn_response == LunchbotMessage.YN_YES_RESPONSE:
            did_bring_lunch = True
        else:
            did_bring_lunch = False

        handle_yes_no_response(lunchbot_message, did_bring_lunch, dynamodb, sc)

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Successfully processed Slack event."})
    }
