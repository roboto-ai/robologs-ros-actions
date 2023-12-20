# What is robologs-ros-actions

`robologs-ros-actions` is an open-source collection of software modules to extract, process and analyze Robot Operating System (ROS) data. These modules, referred to as Actions, are essentially containerized Python scripts, and form part of the broader [robologs](https://github.com/roboto-ai/robologs) library.

Actions can range from simple data transformations to more complex algorithms, accommodating a wide spectrum of requirements and use cases.

The package currently includes the following Actions:

- `get_images_from_rosbag`: Extract images from a rosbag.
- `get_videos_from_rosbag`: Extract videos from a rosbag.
- `get_images_from_videos`: Extract images from common video formats.
- `avi_to_mp4`: Convert .avi videos to the .mp4 format.
- `run_yolov8_rosbag`: Run YOLOv8 object detection algorithm on a rosbag file.
- `run_svo_slam_rosbag`: Run the [SVO SLAM algorithm](https://github.com/uzh-rpg/rpg_svo_pro_open) on a rosbag file.
- `rosbag_info`: Get rosbag metadata.
- `mcap_info`: Get mcap metadata.
- `db3_info`: Get db3 metadata.
- `rosbag_to_csv`: Convert a rosbag to a csv file.
- `rosbag_to_mcap`: Convert a rosbag to a mcap file.
- `merge_rosbags`: Merge multiple rosbags.
- `convert_coco_annotations`: Convert COCO annotation format to Roboto-supported annotation format.
- `parse_rosout_and_tag`: Check /rosout topic for certain strings and tag dataset.
- `rosbag_reindex`: Reindex corrupted rosbag.

# Prerequisites

## Install Docker
- [Install Docker on Linux](https://docs.docker.com/desktop/install/linux-install/)
- [Install Docker on Mac](https://docs.docker.com/desktop/install/mac-install/)
- [Install Docker on Windows](https://docs.docker.com/desktop/install/windows-install/)

## Install pyenv

- [Install pyenv](https://github.com/pyenv/pyenv)

# Quickstart

Try an Action called: `get_images_from_rosbag`:

```bash

# 0. Clone this repository
git clone https://github.com/roboto-ai/robologs-ros-actions.git
cd robologs-ros-actions/actions/get_images_from_rosbag/

# 1. Set up a virtual environment for this project and install dependencies, which includes the `roboto` CLI:
./scripts/setup.sh

# 2. Build the Docker image for the Action: 
./scripts/build.sh

# 3. Run the Action locally: 
./scripts/run.sh <path-to-input-data-directory>

# 4. Run the provided tests to ensure everything is set up correctly:
./scripts/test.sh

# 5. (Optional) Deploy the Action to the Roboto platform (see notes below):
./scripts/deploy.sh

```

Deployment to Roboto (Step 5.) enables you to run an Action at scale on multiple datasets in the cloud, or automatically when new data gets uploaded. You can sign up for a free account at [roboto.ai](https://app.roboto.ai), and find user guides at [docs.roboto.ai](https://docs.roboto.ai/user-guides/index.html).

# Community

We're constantly looking to expand the capabilities of `robologs-ros-actions` and welcome suggestions for new Actions. If you have ideas or need assistance, feel free to join our discussion on [Discord](https://discord.gg/rvXqP6EjwF).

Your contributions and suggestions are not only encouraged but also form an integral part of this open-source initiative. Let's collaborate to make `robologs-ros-actions` more versatile and beneficial for everyone in the ROS community!
