# What is robologs-ros-actions

robologs-ros-actions is a collection of containerized data transformation scripts for ROS data. An *action* is arbitrary code that can be run against a rosbag file to extract, process and analyze data. 

# Quickstart

### Get example rosbag data

```bash
mkdir -p ~/ros_data/output/

cd ~/ros_data/
aws s3 cp s3://roboto-ros-demo-datasets/example_bag_small.bag ./
```

### Build docker image locally
```bash
cd ~/Code/robologs-ros-actions/
./build_docker_image.sh
```

### Alternatively, pull docker image from our registry
```bash
docker pull 778617497685.dkr.ecr.us-west-2.amazonaws.com/robologs-ros-actions:latest
```

### Run docker image
In this example, we will run an action to extract images from a rosbag file. 

```bash
docker run --volume ~/ros_data/:/container/input/ --volume ~/ros_data/output/:/container/output/ robologs-ros-actions 'robologs-ros-utils get-images --input $INPUT_DIR --output $OUTPUT_DIR'
```

### Run python code locally in virtual environment
```bash 
cd ~/Code/robologs-ros-actions/actions/python/

# create virtual environment
conda create -n robo_test python=3.9

conda activate robo_test

# install requirements
pip install -r robologs_ros_actions/requirements.txt

# set environment variables
export INPUT_DIR="~/ros_data/"

export OUTPUT_DIR="~/ros_data/output/"

# run code
python robologs_ros_actions/parse_log_example/parse_log_file.py --input_dir $INPUT_DIR --output_dir $OUTPUT_DIR -d '{\"clock\": \"Subscribing to /clock\"}'
```

## Verify output
```bash
ls ~/ros_data/output/
```
