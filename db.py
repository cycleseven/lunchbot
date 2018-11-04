import os
import uuid
from datetime import datetime
from decimal import Decimal

from services import Dynamo
from boto3.dynamodb.conditions import Key


# TODO: if possible, refactor so these all use the same boto object (ie. always use DynamoTableService).
#       This will allow some code to be deleted in services.py


def get_todays_records_for_user(user_id):
    table = Dynamo.get_table()
    now = datetime.utcnow()
    start_of_today = datetime(now.year, now.month, now.day).timestamp()

    return table.query(
        ConsistentRead=True,
        KeyConditionExpression=Key("user_id").eq(user_id) & Key("timestamp").gte(Decimal(start_of_today))
    )["Items"]


def delete_records(records):
    dynamo_resource = Dynamo.get_resource()
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
    dynamodb_client = Dynamo.get_client()

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
