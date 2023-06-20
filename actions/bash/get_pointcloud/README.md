[### get_pointcloud.sh

This action extracts .pcd files from rosbags with point cloud topics of the type *sensor_msgs/PointCloud2*. 

### Run command

```bash 
./get_pointcloud.sh $INPUT_DIR $OUTPUT_DIR'
```

**Docker run example**

```bash
docker run --volume ~/ros_data/:/container/input/ --volume ~/ros_data/output/:/container/output/ robologs-ros-actions '/function/actions/bash/get_pointcloud/get_pointcloud.sh $INPUT_DIR $OUTPUT_DIR'
```

### Arguments

| Argument | Description           | Required | Default Value | Valid Values                         |
|---------|-----------------------|----------|---------------|--------------------------------------|
| input   | A folder with rosbags | Yes      | None          | String (Path to rosbag input folder) |
| output  | Output directory      | Yes      | None          | String (Path to output directory)    |

### Output structure
The output folder will contain a subfolder for each processed rosbag with a set of .pcd files.

```python
output_folder/
├── rosbag_name_1
│ ├── timestamp.pcd
│ └── ...
├── rosbag_name_2
│ ├── timestamp.pcd
│ └── ...
```
]()