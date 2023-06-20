### get-summary

get-summary is an action that extracts rosbag metadata and saves it as a json file. It is provided as part of the robologs-ros-utils command
line utilities which are preinstalled in the robologs-ros-actions docker image.

### Run command

```bash 
robologs-ros-utils get-summary --input $INPUT_DIR --output $OUTPUT_DIR
```

**Docker run example**

```bash
docker run --volume ~/ros_data/:/container/input/ --volume ~/ros_data/output/:/container/output/ robologs-ros-actions 'robologs-ros-utils get-summary --input $INPUT_DIR --output $OUTPUT_DIR'
```

### Arguments

| Argument    | Description                                                              | Required | Default Value          | Valid Values                             |
|-------------|--------------------------------------------------------------------------|----------|------------------------|------------------------------------------|
| --input     | A single rosbag, or folder with rosbags                                  | Yes      | $INPUT_DIR             | String (Path to rosbag or rosbag folder) |
| --output    | Output directory                                                         | Yes      | $OUTPUT_DIR            | String (Path to output directory)        |
| --file-name | Output image format                                                      | No       | "rosbag_metadata.json" | String (with .json ending)               |

### Output structure
The output folder will contain a json file with the rosbag metadata.
```python
output_folder/
├── rosbag_metadata.json
``` 
