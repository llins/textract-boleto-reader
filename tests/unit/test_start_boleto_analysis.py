from uuid import uuid4
from botocore.stub import ANY
from src.app import start_boleto_analysis

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
