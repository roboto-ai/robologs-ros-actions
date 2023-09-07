#!/bin/bash

# Source the ROS setup script
source /opt/ros/iron/setup.sh

# Run the Python script with all the arguments passed to this script
python3 /db3_info/ "$@"
