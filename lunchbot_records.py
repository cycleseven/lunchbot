import os
import uuid
from datetime import datetime
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key

dynamodb_client = boto3.client("dynamodb")
dynamo_resource = boto3.resource("dynamodb")
table = dynamo_resource.Table(os.environ["DYNAMODB_TABLE"])


def get_todays_records_for_user(user_id):
    now = datetime.utcnow()
    start_of_today = datetime(now.year, now.month, now.day).timestamp()

    return table.query(
        ConsistentRead=True,
        KeyConditionExpression=Key("user_id").eq(user_id) & Key("timestamp").gte(Decimal(start_of_today))
    )["Items"]


def delete_records(records):
    delete_requests = [
        {
            "DeleteRequest": {
                "Key": {
                    "user_id": item["user_id"],
                    "timestamp": item["timestamp"]
                }
            }
        } for item in records
    ]
    return dynamo_resource.batch_write_item(
        RequestItems={
            os.environ["DYNAMODB_TABLE"]: delete_requests
        }
    )


def store_record(ts, user_id, channel_id, did_bring_lunch, emoji):
    return dynamodb_client.put_item(
        TableName=os.environ["DYNAMODB_TABLE"],
        Item={
            "id": {
                "S": str(uuid.uuid4())
            },
            "timestamp": {
                "N": ts
            },
            "slack_ts": {
                "S": ts
            },
            "user_id": {
                "S": user_id
            },
            "channel_id": {
                "S": channel_id
            },
            "did_bring_lunch": {
                "BOOL": did_bring_lunch
            },
            "emoji": {
                "S": emoji
            }
        }
    )
