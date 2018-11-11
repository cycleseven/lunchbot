import uuid
from datetime import datetime
from decimal import Decimal

from boto3.dynamodb.conditions import Key

from lunchbot.services import Dynamo


def get_todays_records_for_user(user_id):
    table = Dynamo.get_table()
    now = datetime.utcnow()
    start_of_today = datetime(now.year, now.month, now.day).timestamp()

    return table.query(
        ConsistentRead=True,
        KeyConditionExpression=Key("user_id").eq(user_id) & Key("timestamp").gte(Decimal(start_of_today))
    )["Items"]


def delete_records(records):
    dynamo_table = Dynamo.get_table()
    with dynamo_table.batch_write() as batch:
        for record in records:
            batch.delete_item(Key={"user_id": record["user_id"], "timestamp": record["timestamp"]})


def store_record(ts, user_id, channel_id, did_bring_lunch, emoji):
    dynamo_table = Dynamo.get_table()

    return dynamo_table.put_item(
        Item={
            "id": str(uuid.uuid4()),
            "timestamp": Decimal(ts),
            "slack_ts": ts,
            "user_id": user_id,
            "channel_id": channel_id,
            "did_bring_lunch": did_bring_lunch,
            "emoji": emoji,
        }
    )
