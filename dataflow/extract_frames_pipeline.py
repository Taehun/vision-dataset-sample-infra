import argparse
import json
import logging

import apache_beam as beam
import apache_beam.pvalue as pvalue
from apache_beam.io import ReadFromText
from apache_beam.options.pipeline_options import PipelineOptions


class GetVideoFiles(beam.DoFn):
    def __init__(self, input_path):
        self.input_path = input_path

    def _get_video_signed_url(self, bucket_name, blob_path, creds):
        import datetime

        from google.cloud import storage
        from google.oauth2 import service_account

        credentials_json = json.loads("\n".join(creds))
        credentials = service_account.Credentials.from_service_account_info(credentials_json)

        client = storage.Client(credentials=credentials)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        return blob.generate_signed_url(datetime.timedelta(seconds=300), method="GET")

    def process(self, message, creds):
        """Get uploaded vidoe files in Google Cloud Storage."""

        import json
        import os.path as osp
        from pathlib import Path

        msg_obj = json.loads(message)

        video_path = "gs://" + str(Path(osp.join(msg_obj["bucket"], msg_obj["name"])))
        video_folder = str(Path(osp.join(msg_obj["bucket"], msg_obj["name"])).parent)

        logging.debug(f"Input Path = {self.input_path}, video_foldet = {video_folder}")

        prefix_len = len("gs://")
        if self.input_path[prefix_len:] == video_folder:
            video_file_url = self._get_video_signed_url(msg_obj["bucket"], msg_obj["name"], creds)

            logging.info(f"GetVideoFiles: Video file = {video_path}")
            logging.info(f"GetVideoFiles: Signed Video URL {video_file_url}")
            yield (video_path, video_file_url)


class ExtractFrames(beam.DoFn):
    def __init__(self, output_path):
        self.output_path = output_path

    def process(self, element):
        import math
        import os.path as osp
        import urllib.request as req

        import cv2

        video_path, video_file_url = element

        logging.info(f"ExtractFrames: {video_path}")
        logging.info(f"ExtractFrames: {video_file_url}")

        _, videoFileName = osp.split(video_path)
        videoID, _ = osp.splitext(videoFileName)
        imagesFolder = f"{self.output_path}/{videoID}"

        logging.debug(
            f"output path = {self.output_path}, videoFileName = {videoFileName}, videoID = {videoID}, imagesFolder = {imagesFolder}"
        )

        # Download a video file from signed URL
        req.urlretrieve(video_file_url, f"/tmp/{videoID}.mp4")

        cap = cv2.VideoCapture(f"/tmp/{videoID}.mp4")
        frameRate = cap.get(5)  # Get frame rate

        while cap.isOpened():
            frameId = cap.get(1)  # Current frame number
            ret, frame = cap.read()
            if ret != True:
                logging.warning("ExtractFrames: Failed to read frame!")
                break

            # Sample the frames each 1 second
            if frameId % math.floor(frameRate) == 0:
                filename = f"{imagesFolder}/{str(int(frameId))}.jpg"

                is_success, buffer = cv2.imencode(".jpg", frame)
                if is_success != True:
                    logging.warning("ExtractFrames: Failed to encoding frame!")
                    continue

                # Write JPG file to GCS
                with beam.io.gcsio.GcsIO().open(filename=filename, mode="wb") as f:
                    f.write(buffer)

                logging.info(f"UploadFrames: {filename}")

        cap.release()


def run(input_topic, vidoe_path, image_path, key_file, pipeline_args=None):
    # Set `save_main_session` to True so DoFns can access globally imported modules.
    pipeline_options = PipelineOptions(pipeline_args, streaming=True, save_main_session=True)

    with beam.Pipeline(options=pipeline_options) as pipeline:
        credentials = pipeline | "Read Credentials from GCS" >> ReadFromText(key_file)

        (
            pipeline
            | "Read from Pub/Sub" >> beam.io.ReadFromPubSub(topic=input_topic)
            | "Get the video files" >> beam.ParDo(GetVideoFiles(vidoe_path), pvalue.AsList(credentials))
            | "Extract video frames" >> beam.ParDo(ExtractFrames(image_path))
        )


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_topic",
        type=str,
        required=True,
        help="The Cloud Pub/Sub topic to read from." '"projects/<PROJECT_ID>/topics/<TOPIC_ID>".',
    )
    parser.add_argument(
        "--video_path",
        type=str,
        required=True,
        help="Path of the video file folder in GCS." "gs://<BUCKET>/<VIDEO_FOLDER>",
    )
    parser.add_argument(
        "--image_path",
        type=str,
        required=True,
        help="Path of the image file folder in GCS." "gs://<BUCKET>/<IMAGE_FOLDER>",
    )
    parser.add_argument("--key_file", required=True, help="Path to service account credentials JSON.")
    known_args, pipeline_args = parser.parse_known_args()

    run(
        known_args.input_topic,
        known_args.video_path,
        known_args.image_path,
        known_args.key_file,
        pipeline_args,
    )
