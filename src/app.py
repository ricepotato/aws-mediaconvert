import json
import logging
import os
import pathlib
import uuid

import boto3

# import requests

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())


def create_media_convert_job(
    s3_src: str, s3_dest: str, region_name: str, user_metadata: dict = {}
):
    log.info(
        "create_media_convert_job src=%s dest=%s region_name=%s",
        s3_src,
        s3_dest,
        region_name,
    )
    mediaconvert_client = boto3.client("mediaconvert", region_name=region_name)
    endpoints = mediaconvert_client.describe_endpoints()

    # add the account-specific endpoint to the client session
    client = boto3.client(
        "mediaconvert",
        region_name=region_name,
        endpoint_url=endpoints["Endpoints"][0]["Url"],
        verify=False,
    )

    job_setting = get_job_setting(s3_src, s3_dest)
    job = client.create_job(
        Role="MediaConvert_Default_Role",
        UserMetadata=user_metadata,
        Settings=job_setting,
    )
    return job


def get_job_setting(source_s3: str, dest_s3: str):
    job_json_path = pathlib.Path(__file__).parent / "job.json"
    with open(job_json_path, "r", encoding="utf-8") as f:
        job_settings = json.loads(f.read())
        job_settings["Inputs"][0]["FileInput"] = source_s3
        job_settings["OutputGroups"][0]["OutputGroupSettings"]["HlsGroupSettings"][
            "Destination"
        ] = dest_s3

    log.info(job_settings)
    return job_settings


def media_created_handler(event, context):
    """s3 에 media 파일이 생성되면 호출된다.
    호출 되는 S3 이름은 sam parameter 의 MediaBucket 값이다.
    이 S3 bucket 에 media/ 에 파일이 생성되면 함수가 호출된다.

    결과는 output/ 에 생성한다.

    """
    src_s3_bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
    src_s3_key = event["Records"][0]["s3"]["object"]["key"]

    asset_id = str(uuid.uuid4())
    source_s3 = f"s3://{src_s3_bucket_name}/{src_s3_key}"
    dest_s3 = f"s3://{os.environ['MEDIA_BUCKET']}/output/{asset_id}"

    job_metadata = {}
    job_metadata["assetID"] = asset_id
    job_metadata["application"] = "onesearch mediaconvert sam"
    job_metadata["input"] = source_s3

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

    with open("job.json", "r", encoding="utf-8") as f:
        job_settings = json.loads(f.read())
        job_settings["Inputs"][0]["FileInput"] = source_s3
        job_settings["OutputGroups"][0]["OutputGroupSettings"]["HlsGroupSettings"][
            "Destination"
        ] = dest_s3

    log.info(job_settings)
    # job = client.create_job(Role=mediaConvertRole, UserMetadata=jobMetadata, Settings=jobSettings)

    return {
        "statusCode": 200,
        "body": json.dumps(job_settings, indent=4, sort_keys=True, default=str),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
    }


def media_convert_job_state_change_handler(event, context):
    log.info(event)

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "hello world",
                # "location": ip.text.replace("\n", "")
            }
        ),
    }
