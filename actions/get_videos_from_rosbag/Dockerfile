FROM robologs/robologs-base-image:0.1

# Install other requirements
COPY requirements.runtime.txt ./
RUN /usr/bin/python3 -m pip install --upgrade pip setuptools && /usr/bin/python3 -m pip install -r requirements.runtime.txt

COPY src/get_videos_from_rosbag/ ./get_videos_from_rosbag

RUN apt-get update && apt install -y git
RUN pip install git+https://github.com/roboto-ai/rosbags-fork.git

ENTRYPOINT [ "python3", "-m", "get_videos_from_rosbag" ]
