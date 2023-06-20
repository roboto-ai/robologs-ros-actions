# Use ros:noetic-ros-core as base image
FROM ros:noetic-ros-core

# Define function directory
ARG FUNCTION_DIR="/function"
ARG INPUT_DIR="/container/input"
ARG OUTPUT_DIR="/container/output"

# Set environment variables
ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONPATH="$PYTHONPATH:/function/actions/python/"
ENV INPUT_DIR=$INPUT_DIR
ENV OUTPUT_DIR=$OUTPUT_DIR

# Set working directory
WORKDIR ${FUNCTION_DIR}

# Install build dependencies
RUN apt-get update && apt-get install -y \
    g++ \
    make \
    cmake \
    unzip \
    libcurl4-openssl-dev \
    python3 \
    python3-pip \
    python-all-dev \
    libexiv2-dev \
    libboost-python-dev \
    ffmpeg \
    libsm6 \
    libxext6 \
    wget \
    ros-noetic-cv-bridge \
    ros-noetic-pcl-ros && \
    rm -rf /var/lib/apt/lists/*  # clean up apt cache to reduce layer size


# Create necessary directories
RUN mkdir -p ${FUNCTION_DIR} ${INPUT_DIR} ${OUTPUT_DIR}
RUN ln -s /usr/bin/python3 /usr/bin/python

# Download the mcap CLI binary using wget
RUN wget https://github.com/foxglove/mcap/releases/latest/download/mcap-linux-amd64 -O /usr/local/bin/mcap

# Make the binary executable
RUN chmod +x /usr/local/bin/mcap

# Copy function code
COPY ./ ${FUNCTION_DIR}

# Install python requirements
RUN pip install --no-cache-dir -r /function/actions/python/robologs_ros_actions/requirements.txt

# Ensure scripts are executable
RUN chmod 777 /opt/ros/noetic/setup.sh && . /opt/ros/noetic/setup.sh
RUN chmod +x /function/actions/bash/get_pointcloud/get_pointcloud.sh
RUN chmod +x /function/actions/bash/convert_ros_to_mcap/convert_ros_to_mcap.sh

ENTRYPOINT ["/bin/bash", "-c"]
