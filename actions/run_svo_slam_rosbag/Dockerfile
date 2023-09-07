# Use ros:noetic-ros-desktop as base image
FROM osrf/ros:noetic-desktop-full

ARG FUNCTION_DIR="/"

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-client \
    python3-catkin-tools \
    python3-vcstool \
    python3-osrf-pycommon \
    libglew-dev \
    libopencv-dev \
    libyaml-cpp-dev \
    libblas-dev \
    liblapack-dev \
    libsuitesparse-dev \
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
    libtool \
    ros-noetic-cv-bridge \
    ros-noetic-rqt-gui \
    ros-noetic-pcl-ros \
    git && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p -m 0600 ~/.ssh && ssh-keyscan -H github.com bitbucket.org >> ~/.ssh/known_hosts && \
    mkdir -p ${FUNCTION_DIR} ${INPUT_DIR} ${OUTPUT_DIR} && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    chmod 777 /opt/ros/noetic/setup.sh && . /opt/ros/noetic/setup.sh

# Clone necessary repositories
RUN mkdir -p ${FUNCTION_DIR}/svo_ws/src && \
    cd ${FUNCTION_DIR}/svo_ws/src && \
    git clone https://github.com/uzh-rpg/rpg_svo_pro_open.git && \
    git clone https://github.com/catkin/catkin_simple.git && \
    git clone https://github.com/zurich-eye/cmake_external_project_catkin.git && \
    git clone https://github.com/ethz-asl/eigen_catkin.git && \
    git clone https://github.com/ethz-asl/eigen_checks.git && \
    git clone https://github.com/uzh-rpg/fast_neon.git && \
    git clone https://github.com/ethz-asl/gflags_catkin.git && \
    git clone https://github.com/ethz-asl/glog_catkin.git && \
    git clone https://github.com/ethz-asl/minkindr.git && \
    git clone https://github.com/ethz-asl/opengv.git && \
    git clone https://github.com/ethz-asl/minkindr_ros.git && \
    git clone https://github.com/ethz-asl/ceres_catkin.git && \
    git clone https://github.com/uzh-rpg/dbow2_catkin.git && \
    sed -i 's|git@github.com:dorian3d/DBoW2.git|https://github.com/dorian3d/DBoW2.git|' ${FUNCTION_DIR}/svo_ws/src/dbow2_catkin/CMakeLists.txt && \
    git clone https://github.com/uzh-rpg/rpg_trajectory_evaluation.git -b dev

# Configuration and building
RUN /bin/bash -c "source /opt/ros/noetic/setup.bash && \
    cd ${FUNCTION_DIR}/svo_ws && \
    catkin config --init --mkdirs --extend /opt/ros/noetic --cmake-args -DCMAKE_BUILD_TYPE=Release -DEIGEN3_INCLUDE_DIR=/usr/include/eigen3 && \
    cd src && \
    touch minkindr/minkindr_python/CATKIN_IGNORE && \
    if [ -d 'rpg_svo_pro_open/svo_online_loopclosing/vocabularies' ]; then cd rpg_svo_pro_open/svo_online_loopclosing/vocabularies && ./download_voc.sh; fi && \
    cd ${FUNCTION_DIR}/svo_ws && \
    catkin build"

COPY src/main.sh /main.sh
COPY src/entry_script.sh /entry_script.sh
COPY src/run_svo_slam.launch /run_svo_slam.launch


# Copy function code and other files
RUN chmod +x /entry_script.sh

ENTRYPOINT ["/entry_script.sh"]
