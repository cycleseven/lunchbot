import json
from pprint import pprint

from lunchbot import Lunchbot
from events import LunchbotMessageEvent


def on_slack_event(event, context):
    """Lambda handler called when a new event from Slack is POSTed."""

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

    lunchbot_message = LunchbotMessageEvent(message_event)

    if not lunchbot_message.is_valid_message():
        return {
            "statusCode": 200,
            "body": "Ignoring non-message event."
        }

    lunchbot = Lunchbot(lunchbot_message)
    lunchbot.react_to_message()

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Successfully processed Slack event."})
    }
