import json
import os
import boto3
from aws_lambda_powertools import Logger, Metrics, Tracer

tracer = Tracer(service="start_boleto_analysis")
logger = Logger()
metrics = Metrics()

session = boto3.Session()
textract = session.client("textract")

textract_notification_topic = os.environ['TEXTRACT_NOTIFICATION_TOPIC']
textract_notification_role = os.environ['TEXTRACT_NOTIFICATION_ROLE']

@metrics.log_metrics(capture_cold_start_metric=True)
@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    try:
        job_ids = []

        for record in event["Records"]:
            s3_event = json.loads(record["Sns"]["Message"])
            for rec in s3_event["Records"]:
                job_id = _start_document_analysis(rec["s3"]["bucket"]["name"], rec["s3"]["object"]["key"], textract_notification_topic, textract_notification_role)
                job_ids.append(job_id)

        response = {"JobIds": job_ids}
        logger.info(response)

        return response
    except Exception as e:
        logger.exception(e)
        raise

def _start_document_analysis(s3_bucket_name, s3_object_name, notification_topic, notification_role):
    response = None
    response = textract.start_document_analysis(
        DocumentLocation={
            "S3Object": {
                "Bucket": s3_bucket_name,
                "Name": s3_object_name
            }
        },
        FeatureTypes=[
            "FORMS"
        ],
        NotificationChannel={
            "SNSTopicArn": notification_topic,
            "RoleArn": notification_role
        }
    )
    return response["JobId"]