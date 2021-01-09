import boto3

def textract():
    return boto3.client("textract")

def sns():
    return boto3.client("sns")