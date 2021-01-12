import json
import re
import os
import boto3
import time
from aws_lambda_powertools import Logger, Metrics, Tracer

tracer = Tracer(service="get_boleto_analysis")
logger = Logger()
metrics = Metrics()

session = boto3.Session()
textract = session.client("textract")
sns = session.client("sns")

analysis_result_topic = os.environ['ANALYSIS_RESULT_TOPIC']

@metrics.log_metrics(capture_cold_start_metric=True)
@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    try:
        responses = []

        for record in event["Records"]:
            
            textract_notification = json.loads(record["Sns"]["Message"])
            analysis = _get_document_analysis(textract_notification["JobId"])
            lines = _get_lines(analysis)
            kv_map = _get_kv_map(analysis)
            kv_map["BarcodeNumber"] = _find_barcode_number(lines)

            response = {
                "DocumentLocation" : textract_notification["DocumentLocation"],
                "KeyValuePairs" : kv_map
            }

            sns.publish(TopicArn=analysis_result_topic, Message=json.dumps(response))

            responses.append(response)

        return responses
    except Exception as e:
        logger.exception(e)
        raise

def _get_document_analysis(job_id):
    pages = []
    response = textract.get_document_analysis(JobId=job_id)
    
    status = response["JobStatus"]
    while(status == "IN_PROGRESS"):
        time.sleep(0.5)
        response = textract.get_document_analysis(JobId=job_id)
        status = response["JobStatus"]

    pages.append(response)
    next_token = None
    if("NextToken" in response):
        next_token = response["NextToken"]

    while(next_token):
        response = textract.get_document_analysis(JobId=job_id, NextToken=next_token)

        pages.append(response)
        next_token = None
        if("NextToken" in response):
            next_token = response["NextToken"]

    return pages

def _get_lines(response):
    lines = []

    for resultPage in response:
        for item in resultPage["Blocks"]:
            if item["BlockType"] == "LINE":
                lines.append(item["Text"])

    return lines

def _get_kv_map(response):
    kv_map = {}
    key_map, value_map, block_map = _get_key_value_block_maps(response)

    for _, key_block in key_map.items():
        value_block = _find_value_block(key_block, value_map)
        key = _get_text(key_block, block_map)
        val = _get_text(value_block, block_map)
        kv_map[key] = val

    return kv_map

def _get_key_value_block_maps(response):
    key_map = {}
    value_map = {}
    block_map = {}

    for page in response:
        for block in page["Blocks"]:
            block_id = block["Id"]
            block_map[block_id] = block
            if block["BlockType"] == "KEY_VALUE_SET":
                if "KEY" in block["EntityTypes"]:
                    key_map[block_id] = block
                else:
                    value_map[block_id] = block

    return key_map, value_map, block_map

def _find_value_block(key_block, value_map):
    for relationship in key_block["Relationships"]:
        if relationship["Type"] == "VALUE":
            for value_id in relationship["Ids"]:
                value_block = value_map[value_id]

    return value_block

def _get_text(result, blocks_map):
    text = ""
    if "Relationships" in result:
        for relationship in result["Relationships"]:
            if relationship["Type"] == "CHILD":
                for child_id in relationship["Ids"]:
                    word = blocks_map[child_id]
                    if word["BlockType"] == "WORD":
                        text += word["Text"] + " "
                    if word["BlockType"] == "SELECTION_ELEMENT":
                        if word["SelectionStatus"] == "SELECTED":
                            text += "X "    
                                
    return text

def _find_barcode_number(lines):
    for line in lines:
        m = re.search(r'^(\d{5})\D*(\d{5})\D*(\d{5})\D*(\d{6})\D*(\d{5})\D*(\d{6})\D*(\d)\D*(\d{14})$', line)
        if(m):
            return "".join(m.groups())

    return ""