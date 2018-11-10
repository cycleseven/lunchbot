import json
from pprint import pprint

from lunchbot.lunchbot import Lunchbot
from lunchbot.events import LunchbotMessageEvent


def on_slack_event(event, context):
    """Lambda handler called when a new event from Slack is POSTed."""

    print("Received event from Slack.")
    pprint(event)

    # Parse
    try:
        lunchbot_message = LunchbotMessageEvent.create_from_api_gateway_event(event)
    except KeyError:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Malformed event in request body."
            })
        }

    # Validate
    if not lunchbot_message.is_valid_message():
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Invalid event, expected a Slack message. https://api.slack.com/events/message"
            })
        }

    lunchbot = Lunchbot(lunchbot_message)
    lunchbot.react_to_message()

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Successfully processed Slack event."})
    }
