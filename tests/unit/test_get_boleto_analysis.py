import pytest
import json
from botocore.stub import Stubber, ANY
from src import get_boleto_analysis

@pytest.fixture
def textract_stub():
    with Stubber(get_boleto_analysis.textract) as stubber:
        yield stubber
        stubber.assert_no_pending_responses()

@pytest.fixture
def sns_stub():
    with Stubber(get_boleto_analysis.sns) as stubber:
        yield stubber
        stubber.assert_no_pending_responses()

@pytest.fixture
def sns_textract_notification():
    with open("./events/sns_textract_notification.json", "r") as fp:
        return json.load(fp)

@pytest.fixture
def textract_response():
    with open("./events/textract_response.json", "r") as fp:
        return json.load(fp)

def test_lambda_handler(sns_textract_notification, lambda_context, textract_response, textract_stub, sns_stub):

    textract_stub.add_response(
        method = "get_document_analysis",
        service_response = textract_response,
        expected_params = {"JobId": ANY}
    )

    sns_stub.add_response(
        method = "publish",
        service_response = {},
        expected_params = {"TopicArn": ANY, "Message": ANY}
    )

    with textract_stub, sns_stub:
        ret = get_boleto_analysis.lambda_handler(sns_textract_notification, lambda_context)

    assert ret[0]["KeyValuePairs"]["BarcodeNumber"] == "23793381286002890582082000063303882800000068040"