FROM robologs/robologs-base-image:0.1

# Install other requirements
RUN /usr/bin/python3 -m pip install --upgrade pip
RUN /usr/bin/python3 -m pip install robologs-ros-utils==0.1.1a76 --extra-index-url https://test.pypi.org/simple/
RUN /usr/bin/python3 -m pip install roboto==0.11.2

# Install ultralytics cpu-only 
RUN /usr/bin/python3 -m pip install torch==1.11.0+cpu torchvision==0.12.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
RUN /usr/bin/python3 -m pip install ultralytics

COPY src/run_yolov8_rosbag/ ./run_yolov8_rosbag

ENTRYPOINT [ "python3", "-m", "run_yolov8_rosbag" ]
