### parse_log_example

This is a simple python-based action that checks the /rosout console log topic for a certain string and then saves a tag to a .json file if it is present. 

### Run command

```bash 
python parse_log_file.py --input_dir $INPUT_DIR --output_dir $OUTPUT_DIR -d '{"tag": "keyword_string"}'
```

**Docker run example**

```bash
docker run --volume ~/ros_data/:/container/input/ --volume ~/ros_data/output/:/container/output/ robologs-ros-actions "python /function/actions/python/robologs_ros_actions/parse_log_example/parse_log_file.py --input_dir /container/input --output_dir /container/output -d '{\"clock\": \"Subscribing to /clock\"}'"
```

### Arguments

| Argument         | Description                                                                     | Required | Default Value   | Valid Values                                                |
|------------------|---------------------------------------------------------------------------------|----------|-----------------|-------------------------------------------------------------|
| `-d`, `--dictionary` | A string that can be converted to a dictionary to search for specific log strings | Yes      | None            | String (Must be convertible to a dictionary). For example: '{\"clock\": \"Subscribing to /clock\"}' |
| `-i`, `--input_dir`  | Directory containing the rosbag or rosbags to be processed                       | No       | $INPUT_DIR      | String (Path to rosbag or rosbag folder)                    |
| `-o`, `--output_dir` | Output directory where results will be stored                                    | No       | $OUTPUT_DIR     | String (Path to output directory)                           |

### Output structure
The output folder will contain a dataset_md_changeset.json file with the following structure:
```python
{"addTags": ["clock"], "removeTags": [], "metadata": {}}
``` 
