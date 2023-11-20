from src import app


def test_create_job(env):
    src_s3 = "s3://cf-simple-s3-origin-ricepotato-cdn-632854243364/media/abc_sbt.mp4"
    dest_s3 = (
        "s3://cf-simple-s3-origin-ricepotato-cdn-632854243364/output/abc_sbt/abc_sbt"
    )

    # src_s3 = "s3://cf-simple-s3-origin-ricepotato-cdn-632854243364/media/MOV03575.MPG"
    # dest_s3 = "s3://cf-simple-s3-origin-ricepotato-cdn-632854243364/output/MOV03575/video"

    meta_data = {
        "src": src_s3,
        "dest": dest_s3,
    }

    job = app.create_media_convert_job(src_s3, dest_s3, "ap-northeast-2", meta_data)
    assert job
