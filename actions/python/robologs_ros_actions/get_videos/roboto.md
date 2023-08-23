---
# GetVideosFromBag

---

## Description

`GetVideosFromBag` is an action that extracts videos from a rosbag file. It's a component of the [robologs-ros-utils](https://github.com/roboto-ai/robologs-ros-utils/) command-line utilities. These utilities come pre-installed in the [robologs/robologs-ros-actions:latest](https://hub.docker.com/repository/docker/robologs/robologs-ros-actions/general) Docker image.

---

## Code Reference

- **Dockerfile**: [View Here](https://github.com/roboto-ai/robologs-ros-actions/blob/main/docker/Dockerfile)
- **Script**: [get_videos.py](https://github.com/roboto-ai/robologs-ros-utils/blob/b07ee72e5b01ab712c5c862351302022ef1e2f5c/python/robologs_ros_utils/sources/ros1/get_videos_from_bag.py#L26)

---

## Run Command

```bash 
robologs-ros-utils get-videos --input $INPUT_DIR --output $OUTPUT_DIR
```

---

## Arguments
The following table details the available command line arguments for this action:

| Argument      | Description                                           | Required | Default Value | Valid Values                                          |
|---------------|-------------------------------------------------------|----------|-------|-------------------------------------------------------|
| --input       | A single rosbag, or folder with rosbags               | Yes      | $INPUT_DIR | String (Path to rosbag or rosbag folder)              |
| --output      | Output directory                                      | Yes      | $OUTPUT_DIR | String (Path to output directory)                     |
| --format      | Output image format                                   | No       | "jpg" | String (e.g., "jpg", "png")                           |
| --manifest    | SaveOutput manifest.json with timestamps and metadata | No       | False | True if set                                           |
| --save-images | Save images if set                                    | No       | None  | True if set                                           |
| --topics      | Topic names used for extraction, comma-separated list | No       | None (will extract all image topics) | String (comma-separated list of topics)               |
| --naming      | Naming convention for output images                   | No       | "sequential" | "rosbag_timestamp", "msg_timestamp", "sequential"     |
| --resize      | Resize image to width,height                          | No       | None  | String (width,height)                                 |
| --sample      | Only extract every n-th frame                         | No       | None  | Integer                                               |
| --start_time  | Only extract from start time                          | No       | None  | Float (timestamp in seconds since start of recording) |
| --end_time    | Only extract until end time                           | No       | None  | (timestamp in seconds since start of recording)       |

---

## Output Folder Structure
The output folder will contain a subfolder for each image topic with the extracted videos, images and a manifest.json file with timestamps and metadata.

```python
output_folder/
├── image_topic_name 1
│ ├── image_topic_name_1_000000.jpg
│ └── image_topic_name_1_000001.jpg
│ └── ...
│ └── video.mp4
│ └── img_manifest.json
├── image_topic_name 2
│ ├── image_topic_name_2_000000.jpg
│ └── image_topic_name_2_000001.jpg
│ └── ...
│ └── video.mp4
│ └── img_manifest.json
├── ...
```

---

## Running Locally
Pull the [robologs/robologs-ros-actions:latest](https://hub.docker.com/repository/docker/robologs/robologs-ros-actions/general) Docker image:

```bash
docker pull robologs/robologs-ros-actions:latest
```
Execute the Action. Make sure you adapt the paths to your local system:

```bash
docker run --volume ~/YOUR_ROS_DATA/input/:/container/input/ --volume ~/YOUR_ROS_DATA/output/:/container/output/ robologs-ros-actions 'robologs-ros-utils get-videos --input $INPUT_DIR --output $OUTPUT_DIR'
```