import datetime
import json
from pprint import pformat

from lunchbot import logging, db, monthly_report
from lunchbot.lunchbot import Lunchbot
from lunchbot.events import LunchbotMessageEvent, ScheduledTaskOptions
from lunchbot.services import Dynamo, Slack

logger = logging.get_logger(__name__)


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
            "body": json.dumps({"message": "Malformed event in request body."}),
        }

    # Validate
    if not lunchbot_message.is_valid_message():
        return {
            "statusCode": 400,
            "body": json.dumps(
                {
                    "message": (
                        "Unhandled event format. "
                        "Expected a Slack message (https://api.slack.com/events/message). "
                        "Note that message_delete and bot_message events are intentionally unhandled."
                    )
                }
            ),
        }

    lunchbot = Lunchbot(lunchbot_message)
    lunchbot.react_to_message()

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Successfully processed Slack event."}),
    }


def generate_monthly_report(event, _context):
    logger.info(f"Generating monthly report with options: {event}")

    slack_client = Slack.get_client()

    # Find out which channels the bot belongs to
    conversations_response = slack_client.api_call(
        "users.conversations", exclude_archived=True, limit=10
    )

    logger.debug("")
    logger.debug(pformat(conversations_response))

    # Check if more than 10 channels were returned.
    #
    # This is a hard limit enforced by the app to prevent too many channels from
    # increasing memory used/execution time/complexity of monthly report solution.
    next_cursor = conversations_response.get("response_metadata", {}).get("next_cursor")
    assert next_cursor == ""

    # Check that at least one channel was returned
    if len(conversations_response["channels"]) == 0:
        logger.warning(
            "The bot user hasn't been added to any channels, so no monthly reports will be posted."
        )
        return

    channels = [channel["id"] for channel in conversations_response["channels"]]
    logger.info(f"Bot found in channels: {channels}")

    options = ScheduledTaskOptions.create_from_cloudwatch_event(event)

    for channel in channels:
        records = db.get_monthly_records_for_channel(channel)
        users = monthly_report.fetch_users(records)
        stats = monthly_report.get_monthly_stats(records, users)

        if len(stats) == 0:
            logger.warning(f"No stats found for this month in channel {channel}.")
            return

        summary = monthly_report.summarise_results(stats)

        logger.info(f"Summary for channel {channel}")
        logger.info(summary)

        # Don't post the results to Slack on a dry run.
        #
        # The dry run flag allows silent manual testing of the monthly report
        # using the real data gathered for the month.
        if options.is_dry_run():
            continue

        slack_client.api_call("chat.postMessage", channel=channel, text=summary)


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
            logger.info(pformat({**record, "month": month_key}))

            batch.put_item(Item={**record, "month": month_key})
