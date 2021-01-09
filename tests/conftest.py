import json
import os
from uuid import uuid4
import pytest
from unittest.mock import patch
import boto3
from botocore.stub import Stubber, ANY

class MockContext(object):
    def __init__(self, function_name):
        self.function_name = function_name
        self.function_version = "v$LATEST"
        self.memory_limit_in_mb = 512
        self.invoked_function_arn = f"arn:aws:lambda:us-east-1:ACCOUNT:function:{self.function_name}"
        self.aws_request_id = str(uuid4())

@pytest.fixture
def lambda_context():
    return MockContext("dummy_function")

@pytest.fixture()
def sns_s3_put_event_notification():
    with open("./events/sns_s3_put_event_notification.json", "r") as fp:
        return json.load(fp)

@pytest.fixture()
def sns_textract_notification():
    with open("./events/sns_textract_notification.json", "r") as fp:
        return json.load(fp)

@pytest.fixture()
def textract_response():
    with open("./events/textract_response.json", "r") as fp:
        return json.load(fp)

@pytest.fixture()
def textract_stub():
    textract = boto3.client("textract")
    stubber = Stubber(textract)

    with patch("src.app.utils.client.textract", return_value=textract):
        yield stubber

@pytest.fixture()
def sns_stub():
    sns = boto3.client("sns")
    stubber = Stubber(sns)

    with patch("src.app.utils.client.sns", return_value=sns):
        yield stubber