### get-images

get-images is an action that extracts images from a rosbag file. It is provided as part of the robologs-ros-utils command 
line utilities which are preinstalled in the robologs-ros-actions docker image.

### Run command

```bash 
robologs-ros-utils get-images --input $INPUT_DIR --output $OUTPUT_DIR
```

**Docker run example**

```bash
docker run --volume ~/ros_data/:/container/input/ --volume ~/ros_data/output/:/container/output/ robologs-ros-actions 'robologs-ros-utils get-images --input $INPUT_DIR --output $OUTPUT_DIR'
```

### Arguments

| Argument     | Description                                                              | Required | Default Value                        | Valid Values                                          |
|--------------|--------------------------------------------------------------------------|----------|--------------------------------------|-------------------------------------------------------|
| --input      | A single rosbag, or folder with rosbags                                  | Yes      | $INPUT_DIR                           | String (Path to rosbag or rosbag folder)              |
| --output     | Output directory                                                         | Yes      | $OUTPUT_DIR                          | String (Path to output directory)                     |
| --format     | Output image format                                                      | No       | "jpg"                                | String (e.g., "jpg", "png")                           |
| --manifest   | Save manifest.json with timestamps and metadata                          | No       | False                                | True if set                                           |
| --topics     | Topic names used for extraction, comma-separated list                     | No       | None (will extract all image topics) | String (comma-separated list of topics)               |
| --naming     | Naming convention for output images                                      | No       | "sequential"                         | "rosbag_timestamp", "msg_timestamp", "sequential"     |
| --resize     | Resize image to width,height                                             | No       | None                                 | String (width,height)                                 |
| --sample     | Only extract every n-th frame                                            | No       | None                                 | Integer                                               |
| --start_time | Only extract from start time                                             | No       | None                                 | Float (timestamp in seconds since start of recording) |
| --end_time   | Only extract until end time                                              | No       | None                                 | (timestamp in seconds since start of recording)       |


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
