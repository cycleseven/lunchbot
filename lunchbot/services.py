import os

import boto3
from slackclient import SlackClient

from lunchbot import logging


logger = logging.getLogger(__name__)


class Slack(object):
    client = None

    @staticmethod
    def get_client():
        if Slack.client is not None:
            logger.debug("Using cached Slack client")
            return Slack.client

        logger.debug("Creating fresh Slack client")
        slack_token = os.environ["SLACK_API_TOKEN"]
        Slack.client = SlackClient(slack_token)
        return Slack.client


class Dynamo(object):
    table = None

    @staticmethod
    def get_table():
        if Dynamo.table is not None:
            logger.debug("Using cached DynamoDB client")
            return Dynamo.table

        logger.debug("Creating fresh DynamoDB client")
        dynamo_resource = boto3.resource("dynamodb")
        Dynamo.table = dynamo_resource.Table(os.environ["DYNAMODB_TABLE"])
        return Dynamo.table
