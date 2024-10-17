FROM robologs/robologs-base-image:0.1

# Install other requirements
RUN /usr/bin/python3 -m pip install --upgrade pip
RUN /usr/bin/python3 -m pip install robologs-ros-utils==0.1.1a76 --extra-index-url https://test.pypi.org/simple/
RUN /usr/bin/python3 -m pip install roboto==0.11.2

COPY src/get_images_from_rosbag/ ./get_images_from_rosbag

ENTRYPOINT [ "python3", "-m", "get_images_from_rosbag" ]
