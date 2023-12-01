import json
import logging
import os
import pathlib
import uuid

import boto3


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())


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
        Role="arn:aws:iam::632854243364:role/service-role/MediaConvert_Default_Role",
        UserMetadata=user_metadata,
        Settings=job_setting,
    )
    return job


def media_created_handler(event, context):
    """s3 에 media 파일이 생성되면 호출된다.
    호출 되는 S3 이름은 sam parameter 의 MediaBucket 값이다.
    이 S3 bucket 에 media/ 에 파일이 생성되면 함수가 호출된다.

    결과는 output/ 에 생성한다.

    """

    log.info("media_created_handler event: %s", json.dumps(event, indent=4))
    src_s3_bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
    src_s3_key = event["Records"][0]["s3"]["object"]["key"]

    log.info("media created. bucket=%s key=%s", src_s3_bucket_name, src_s3_key)
    asset_id = str(uuid.uuid4())
    source_s3 = f"s3://{src_s3_bucket_name}/{src_s3_key}"
    dest_s3 = f"s3://{os.environ['MEDIA_OUTPUT_BUCKET']}/output/{asset_id}/video"

    log.info("dest s3: %s", dest_s3)

    job_metadata = {}
    job_metadata["assetID"] = asset_id
    job_metadata["application"] = "onesearch mediaconvert sam"
    job_metadata["input"] = source_s3
    job_metadata["output"] = dest_s3

    log.info("job metadata: %s", json.dumps(job_metadata, indent=4))
    region_name = os.environ["MEDIA_CONVERT_REGION"]

    job = create_media_convert_job(source_s3, dest_s3, region_name, job_metadata)

    log.info("job created. job=%s", json.dumps(job, indent=4))

    return {
        "statusCode": 200,
        "body": json.dumps(job, indent=4, sort_keys=True, default=str),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
    }


def media_convert_job_state_change_handler(event, context):
    """
    event example:
    {
      "version": "0",
      "id": "7fb4aa47-dc53-891a-065f-810d8d7ac690",
      "detail-type": "MediaConvert Job State Change",
      "source": "aws.mediaconvert",
      "account": "632854243364",
      "time": "2023-12-01T09:52:14Z",
      "region": "ap-northeast-2",
      "resources": [
        "arn:aws:mediaconvert:ap-northeast-2:632854243364:jobs/1701424327145-85oi69"
      ],
      "detail": {
        "timestamp": 1701424334484,
        "accountId": "632854243364",
        "queue": "arn:aws:mediaconvert:ap-northeast-2:632854243364:queues/Default",
        "jobId": "1701424327145-85oi69",
        "status": "COMPLETE",
        "userMetadata": {
          "assetID": "daa6a1ab-f7bc-4459-9ed6-f490d00d0521",
          "application": "onesearch mediaconvert sam",
          "input": "s3://ricepotato-media-convert-ap-northeast-2/media/nyan_cat.mp4"
        },
        "outputGroupDetails": [
          {
            "outputDetails": [
              {
                "outputFilePaths": [
                  "s3://cf-simple-s3-origin-ricepotato-cdn-632854243364/output/daa6a1ab-f7bc-4459-9ed6-f490d00d0521_720.m3u8"
                ],
                "durationInMs": 804,
                "videoDetails": {
                  "widthInPx": 1280,
                  "heightInPx": 720,
                  "averageBitrate": 4310208
                }
              }
            ],
            "playlistFilePaths": [
              "s3://cf-simple-s3-origin-ricepotato-cdn-632854243364/output/daa6a1ab-f7bc-4459-9ed6-f490d00d0521.m3u8"
            ],
            "type": "HLS_GROUP"
          }
        ],
        "paddingInserted": 0,
        "blackVideoDetected": 0,
        "warnings": [
          { "code": 230001, "count": 1 },
          { "code": 230005, "count": 1 }
        ]
      }
    }

    """
    log.info(event)
    return {
        "statusCode": 200,
        "body": json.dumps(event, indent=4),
    }
