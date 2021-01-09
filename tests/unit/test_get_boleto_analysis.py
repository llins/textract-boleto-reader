import json
from botocore.stub import ANY
from src.app import get_boleto_analysis

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