FROM apache/beam_python3.8_sdk:2.40.0

RUN apt-get update && apt-get install -y --no-install-recommends \
  ffmpeg=7:4.3.4-0+deb11u1 \
  libsm6=2:1.2.3-1 \
  libxext6=2:1.3.3-1.1 \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install -U pip && pip install --no-cache-dir \
  opencv-python==4.6.0.66 \
  google-cloud-storage==2.4.0 \
  google-cloud-pubsub==2.13.4