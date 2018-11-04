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


class DynamoTable(object):
    table = None

    @staticmethod
    def get_table():
        if DynamoTable.table is not None:
            return DynamoTable.table

        dynamo_resource = boto3.resource("dynamodb")
        DynamoTable.table = dynamo_resource.Table(os.environ["DYNAMODB_TABLE"])
        return DynamoTable.table


# TODO: see if we can get rid of this by refactoring db.py
class DynamoClient(object):
    client = None

    @staticmethod
    def get_client():
        if DynamoTable.client is not None:
            return DynamoTable.client

        DynamoTable.client = boto3.client("dynamodb")
        return DynamoTable.client


# TODO: see if we can get rid of this by refactoring db.py
class DynamoResource(object):
    resource = None

    @staticmethod
    def get_resource():
        if DynamoTable.resource is not None:
            return DynamoTable.resource

        DynamoTable.resource = boto3.resource("dynamodb")
        return DynamoTable.resource
