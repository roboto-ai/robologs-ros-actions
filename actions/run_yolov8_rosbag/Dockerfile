FROM robologs/robologs-base-image:0.1

# Install other requirements
COPY requirements.runtime.txt ./
RUN /usr/bin/python3 -m pip install --upgrade pip setuptools && /usr/bin/python3 -m pip install -r requirements.runtime.txt

# Install ultralytics cpu-only 
RUN /usr/bin/python3 -m pip install torch==1.11.0+cpu torchvision==0.12.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
RUN /usr/bin/python3 -m pip install ultralytics

RUN apt-get update && apt install -y git
RUN pip install git+https://github.com/roboto-ai/rosbags-fork.git

COPY src/run_yolov8_rosbag/ ./run_yolov8_rosbag

ENTRYPOINT [ "python3", "-m", "run_yolov8_rosbag" ]
