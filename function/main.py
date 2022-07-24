import base64
import json
import os
from pathlib import Path

def request_labeling(event, context):
     """Triggered from a message on a Cloud Pub/Sub topic.
     Args:
          event (dict): Event payload.
          context (google.cloud.functions.Context): Metadata for the event.
     """
     pubsub_message = base64.b64decode(event['data']).decode('utf-8')
     event_obj = json.loads(pubsub_message)

     bucket = os.environ["BUCKET"]
     image_path = os.environ["IMAGE_PATH"]
     print(bucket, image_path)
     
     # Check the image file upload event
     if bucket == event_obj["bucket"] and image_path == str(Path(event_obj["name"]).parent):
          print(f"{event_obj['name']} file is uploaded!")

          # TODO: Request labeling task to the labeling system(or company)
