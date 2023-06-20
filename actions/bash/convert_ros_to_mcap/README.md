### convert_ros_to_mcap.sh

This action extracts converts rosbags (.bag) files to mcap (.mcap) files.

### Run command

```bash 
./convert_ros_to_mcap.sh $INPUT_DIR $OUTPUT_DIR'
```

**Docker run example**

```bash
docker run --volume ~/ros_data/:/container/input/ --volume ~/ros_data/output/:/container/output/ robologs-ros-actions '/function/actions/bash/convert_ros_to_mcap/convert_ros_to_mcap.sh $INPUT_DIR $OUTPUT_DIR'
```

### Arguments

| Argument | Description                  | Required | Default Value | Valid Values                         |
|---------|------------------------------|----------|---------------|--------------------------------------|
| input   | A folder with rosbags        | Yes      | None          | String (Path to rosbag input folder) |
| output  | Output folder for mcap files | Yes      | None          | String (Path to output directory)    |

### Output structure
The output folder will contain a mcap file for each converted rosbag.

```python
output_folder/
├── rosbag_name_1.mcap
├── rosbag_name_2.mcap
└── ...
```
