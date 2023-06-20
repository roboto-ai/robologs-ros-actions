### get-csv-data-from-bag

get-csv-data-from-bag is an action that converts ROS topics into .csv files. It is provided as part of the robologs-ros-utils command
line utilities which are preinstalled in the robologs-ros-actions docker image.

### Run command

```bash 
robologs-ros-utils get-csv-data-from-bag --input $INPUT_DIR --output $OUTPUT_DIR
```

**Docker run example**

```bash
docker run --volume ~/ros_data/:/container/input/ --volume ~/ros_data/output/:/container/output/ robologs-ros-actions 'robologs-ros-utils get-csv-data-from-bag --input $INPUT_DIR --output $OUTPUT_DIR'
```

### Arguments

| Argument    | Description                                                              | Required | Default Value | Valid Values                                    |
|-------------|--------------------------------------------------------------------------|----------|---------------|-------------------------------------------------|
| --input     | A single rosbag, or directory containing rosbags                          | Yes      | None          | String (Path to rosbag or rosbag folder)        |
| --output    | Output directory for CSV files                                           | Yes      | None          | String (Path to output directory)               |
| --topics    | Comma-separated list of topics to extract                                | No       | None          | String (Comma-separated list of topic names)    |

### Output structure
The output folder will contain a subfolder for each processed rosbag with a collection of per-topic .csv files.

```python
output_folder/
├── rosbag_name_1
│ ├── topic_1.csv
│ └── ...
├── rosbag_name_2
│ ├── topic_1.csv
│ └── ...
├── ...
```
