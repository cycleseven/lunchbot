import os

import boto3
from slackclient import SlackClient


class Slack(object):
    client = None

    @staticmethod
    def get_client():
        if Slack.client is not None:
            return Slack.client

        slack_token = os.environ["SLACK_API_TOKEN"]
        Slack.client = SlackClient(slack_token)
        return Slack.client


# TODO: see about getting rid of client (in favour of using table everywhere)
class Dynamo(object):
    client = None
    table = None

    @staticmethod
    def get_table():
        if Dynamo.table is not None:
            return Dynamo.table

        dynamo_resource = boto3.resource("dynamodb")
        Dynamo.table = dynamo_resource.Table(os.environ["DYNAMODB_TABLE"])
        return Dynamo.table

    @staticmethod
    def get_client():
        if Dynamo.client is not None:
            return Dynamo.client

        Dynamo.client = boto3.client("dynamodb")
        return Dynamo.client
