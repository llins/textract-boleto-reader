import pytest
import json
from uuid import uuid4
from botocore.stub import Stubber, ANY
from src import start_boleto_analysis

@pytest.fixture
def textract_stub():
    with Stubber(start_boleto_analysis.textract) as stubber:
        yield stubber
        stubber.assert_no_pending_responses()

@pytest.fixture
def sns_s3_put_event_notification():
    with open("./events/sns_s3_put_event_notification.json", "r") as fp:
        return json.load(fp)

def test_lambda_handler(sns_s3_put_event_notification, lambda_context, textract_stub):

    jobId = str(uuid4())

    textract_stub.add_response(
        method = "start_document_analysis",
        service_response = {"JobId" : jobId},
        expected_params = {"DocumentLocation": ANY, "FeatureTypes": ANY, "NotificationChannel": ANY}
    )

    with textract_stub:
        ret = start_boleto_analysis.lambda_handler(sns_s3_put_event_notification, lambda_context)

    assert ret == {"JobIds": [jobId]}
