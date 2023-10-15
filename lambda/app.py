import json
import os
import uuid
import boto3
import logging

# import requests

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())


def media_created_handler(event, context):
    """s3 에 media 파일이 생성되면 호출된다.
    호출 되는 S3 이름은 sam parameter 의 MediaBucket 값이다.
    이 S3 bucket 에 media/ 에 파일이 생성되면 함수가 호출된다.

    결과는 output/ 에 생성한다.

    """
    assetID = str(uuid.uuid4())
    src_s3_bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
    src_s3_key = event["Records"][0]["s3"]["object"]["key"]

    source_s3 = f"s3://{src_s3_bucket_name}/{src_s3_key}"
    dest_s3 = f"s3://{os.environ['MEDIA_BUCKET']}/{assetID}"

    jobMetadata = {}
    jobMetadata["assetID"] = assetID
    jobMetadata["application"] = "onesearch mediaconvert sam"
    jobMetadata["input"] = source_s3

    region_name = os.environ["AWS_REGION"]
    # get the account-specific mediaconvert endpoint for this region
    mediaconvert_client = boto3.client("mediaconvert", region_name=region_name)
    endpoints = mediaconvert_client.describe_endpoints()

    # add the account-specific endpoint to the client session
    client = boto3.client(
        "mediaconvert",
        region_name=region_name,
        endpoint_url=endpoints["Endpoints"][0]["Url"],
        verify=False,
    )

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "hello world",
                # "location": ip.text.replace("\n", "")
            }
        ),
    }


def media_convert_job_state_change_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)

    #     raise e

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "hello world",
                # "location": ip.text.replace("\n", "")
            }
        ),
    }
