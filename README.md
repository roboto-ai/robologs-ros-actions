# What is robologs-ros-actions


`robologs-ros-actions` is an open-source toolkit offering a suite of containerized data transformation scripts specifically designed for ROS (Robot Operating System) data. These utilities, referred to as Actions, are essentially encapsulated code scripts that can be executed on a collection of files for various purposes such as data extraction, processing, and analysis.

These Actions can range from straightforward data transformations to more sophisticated algorithms, accommodating a wide spectrum of requirements and complexities.



The package presently includes the following Actions:

- `get_images_from_rosbag`: Extract images from a rosbag.
- `get_videos_from_rosbag`: Extract videos from a rosbag.
- `run_yolov8_rosbag`: Run YOLOv8 object detection algorithm on a rosbag file.
- `run_svo_slam_rosbag`: Run the [SVO SLAM algorithm](https://github.com/uzh-rpg/rpg_svo_pro_open) on a rosbag file.
- `rosbag_info`: Get rosbag metadata.
- `mcap_info`: Get mcap metadata.
- `db3_info`: Get db3 metadata.
- `rosbag_to_csv`: Convert a rosbag to a csv file.
- `rosbag_to_mcap`: Convert a rosbag to a mcap file.

# Pre-requisites

## Install Docker
- [Install Docker on Linux](https://docs.docker.com/desktop/install/linux-install/)
- [Install Docker on Mac](https://docs.docker.com/desktop/install/mac-install/)
- [Install Docker on Windows](https://docs.docker.com/desktop/install/windows-install/)

## Install pyenv

- [Install pyenv](https://github.com/pyenv/pyenv)

# Quickstart

Try the 'get_images_from_rosbag' Action:

```bash

# 0. Clone this repository
git clone https://github.com/roboto-ai/robologs-ros-actions.git
cd robologs-ros-actions/actions/get_images_from_rosbag/

# 1. Set up a virtual environment for this project and install the necessary development dependencies, which includes the `roboto` CLI:
./scripts/setup.sh

# 2. Build the Docker image for the Action: 
./scripts/build.sh

# 3. Execute the Action image locally: 
./scripts/run.sh <path-to-input-data-directory>

# 4. Run the provided tests to ensure everything is set up correctly: 
./scripts/test.sh

# 5. Optionally, you can deploy the Action to the Roboto Platform: 
./scripts/deploy.sh

```

# Community

We are constantly looking to expand the capabilities of robologs-ros-actions and we welcome suggestions for new Actions. If you have ideas or need assistance, feel free to join our discussion on [Discord](https://discord.gg/rvXqP6EjwF).

Your contributions and suggestions are not only encouraged but also form an integral part of this open-source initiative. Let's collaborate to make robologs-ros-actions more versatile and beneficial for everyone in the ROS community!
