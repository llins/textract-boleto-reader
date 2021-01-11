import json
import re
import os
import boto3
from aws_lambda_powertools import Logger, Metrics, Tracer
from .utils import textract, client

tracer = Tracer(service="get_bankslip_analysis")
logger = Logger()
metrics = Metrics()

session = boto3.Session()

analysis_result_topic = os.environ['ANALYSIS_RESULT_TOPIC']

@metrics.log_metrics(capture_cold_start_metric=True)
@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: any):
    try:
        responses = []

        for record in event["Records"]:
            
            textract_notification = json.loads(record["Sns"]["Message"])
            analysis = textract.get_document_analysis(textract_notification["JobId"])
            lines = textract.get_lines(analysis)
            kv_map = textract.get_kv_map(analysis)
            kv_map["BarcodeNumber"] = find_barcode_number(lines)

            response = {
                "DocumentLocation" : textract_notification["DocumentLocation"],
                "KeyValuePairs" : kv_map
            }

            sns = client.sns()
            sns.publish(TopicArn=analysis_result_topic, Message=json.dumps(response))

            responses.append(response)

        return responses
    except Exception as e:
        logger.exception(e)
        raise

def find_barcode_number(lines):
    for line in lines:
        m = re.search(r'^(\d{5})\D*(\d{5})\D*(\d{5})\D*(\d{6})\D*(\d{5})\D*(\d{6})\D*(\d)\D*(\d{14})$', line)
        if(m):
            return "".join(m.groups())

    return ""