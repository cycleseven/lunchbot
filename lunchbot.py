import boto3
import json
import os
import uuid
from slackclient import SlackClient

slack_token = os.environ["SLACK_API_TOKEN"]
sc = SlackClient(slack_token)
dynamodb = boto3.client("dynamodb")


def on_slack_event(event, context):
    try:
        body = json.loads(event["body"])
        payload = body["event"]
        print(body)
    except KeyError:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Malformed event in request body."
            })
        }

    if payload["type"] != "message":
        return {
            "statusCode": 200,
            "body": "Ignoring non-message event."
        }

    if payload["text"].lower() == "yes":
        print("Affirmative response detected using complex deep neural net algorithm.")
        dynamo_response = dynamodb.put_item(
            TableName=os.environ['DYNAMODB_TABLE'],
            Item={
                "id": {
                    "S": str(uuid.uuid4())
                },
                "user": {
                    "S": payload["user"]
                },
                "didBringLunch": {
                    "BOOL": True
                }
            }
        )
        print(dynamo_response)
        sc.api_call(
            "reactions.add",
            channel=payload["channel"],
            name="thumbsup",
            timestamp=payload["ts"]
        )

    return {
        "statusCode": 200,
        "body": json.dumps({"cool": "stuff"})
    }
