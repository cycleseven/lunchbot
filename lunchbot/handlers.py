import datetime
import json
from pprint import pformat

from lunchbot import logging, db, monthly_report
from lunchbot.lunchbot import Lunchbot
from lunchbot.events import LunchbotMessageEvent
from lunchbot.services import Dynamo

logger = logging.getLogger(__name__)


def on_slack_event(event, _context):
    """Lambda handler called when a new event from Slack is POSTed."""

    logger.debug("Received event from Slack.")
    logger.debug(pformat(event))

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


def generate_monthly_report(_event, _context):
    # Pull all records that match the following criteria:
    #   * from this month
    #   * from the #haveyoubroughtlunch channel

    # Find the distinct users in the records
    # For each distinct user, get their info (ratio, money saved and name)
    # Work out who the winner is
    # Generate a message template, using generated stats + a random selection of fun strings
    # Post the message to #haveyoubroughtlunch
    logger.info("Generating monthly report")

    records = db.get_monthly_records()
    users = monthly_report.get_distinct_users(records)

    stats = []
    for user in users:
        user_records = [record for record in records if record["user_id"] == user]
        stats.append({
            "name": monthly_report.fetch_user_name(user),
            "good_days": monthly_report.count_good_days(user_records),
            "total_days": monthly_report.count_distinct_days(records),
            "estimated_money_saved": monthly_report.estimate_money_saved(user_records),
        })

    logger.info("Generated stats")
    logger.info(pformat(stats))


def record_months(_event, _context):
    """One-off script to update all existing records with month"""
    dynamo_table = Dynamo.get_table()
    records = dynamo_table.scan()

    logger.info("Updating records")
    logger.info(pformat(records))

    with dynamo_table.batch_writer() as batch:
        for record in records["Items"]:
            date = datetime.datetime.utcfromtimestamp(record["timestamp"]).date()
            month_key = f"{date.month}/{date.year}"

            logger.info("Writing...")
            logger.info(pformat({
                **record,
                "month": month_key
            }))

            batch.put_item(Item={
                **record,
                "month": month_key
            })
