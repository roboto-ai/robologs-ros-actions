### clip-rosbag

clip-rosbag is an action that can clip/trim a rosbag based on topics and timestamps. It is provided as part of the robologs-ros-utils command 
line utilities which are preinstalled in the robologs-ros-actions docker image.

### Run command

```bash 
robologs-ros-utils clip-rosbag --input $INPUT_DIR --output $OUTPUT_DIR
```

**Docker run example**

```bash
docker run --volume ~/ros_data/:/container/input/ --volume ~/ros_data/output/:/container/output/ robologs-ros-actions 'robologs-ros-utils get-images --input $INPUT_DIR --output $OUTPUT_DIR'
```

### Arguments

| Argument         | Description                                                   | Required | Default Value | Valid Values                                                                                         |
|------------------|---------------------------------------------------------------|----------|---------------|------------------------------------------------------------------------------------------------------|
| --input          | A single rosbag, or folder with rosbags                       | Yes      | $INPUT_DIR    | String (Path to rosbag or rosbag folder)                                                             |
| --output         | Output directory                                              | Yes      | $OUTPUT_DIR   | String (Path to output directory)                                                                    |
| --topics         | Topic names used for extraction, comma-separated list         | No       | None          | String (comma-separated list of topics)                                                              |
| --start-time     | Only extract from start time                                  | No       | None          | Float                                                                                                |
| --end-time       | Only extract until end time                                   | No       | None          | Float                                                                                                |
| --timestamp_type | Type of timestamp used for start-time, end-time specification | No       | offset_s      | rosbag_ns (rosbag timestamp in nanoseconds) or offset_s (offset since start of recording in seconds) |


### Output structure
The output folder will contain a subfolder for each image topic with the extracted images and a manifest.json file with timestamps and metadata.

```python
output_folder/
├── image_topic_name 1
│ ├── image_topic_name_1_000000.jpg
│ └── image_topic_name_1_000001.jpg
│ └── ...
│ └── img_manifest.json
├── image_topic_name 2
│ ├── image_topic_name_2_000000.jpg
│ └── image_topic_name_2_000001.jpg
│ └── ...
│ └── img_manifest.json
├── ...
```
