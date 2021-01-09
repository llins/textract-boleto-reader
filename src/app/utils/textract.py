import time
import json
from . import client

def start_document_analysis(s3_bucket_name, s3_object_name, notification_topic, notification_role):
    response = None
    textract = client.textract()
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

def get_document_analysis(job_id):
    pages = []
    textract = client.textract()
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

def get_lines(response):
    lines = []

    for resultPage in response:
        for item in resultPage["Blocks"]:
            if item["BlockType"] == "LINE":
                lines.append(item["Text"])

    return lines

def get_kv_map(response):
    kv_map = {}
    key_map, value_map, block_map = __get_key_value_block_maps(response)

    for _, key_block in key_map.items():
        value_block = __find_value_block(key_block, value_map)
        key = __get_text(key_block, block_map)
        val = __get_text(value_block, block_map)
        kv_map[key] = val

    return kv_map

def __get_key_value_block_maps(response):
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

def __find_value_block(key_block, value_map):
    for relationship in key_block["Relationships"]:
        if relationship["Type"] == "VALUE":
            for value_id in relationship["Ids"]:
                value_block = value_map[value_id]

    return value_block

def __get_text(result, blocks_map):
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