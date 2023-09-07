#!/bin/bash

source /opt/ros/noetic/setup.bash
source /svo_ws/devel/setup.bash

# Read input and output directories from environment variables
ROBOTO_INPUT_DIR="${ROBOTO_INPUT_DIR:-/input}" # default to /input if variable not set
ROBOTO_OUTPUT_DIR="${ROBOTO_OUTPUT_DIR:-/output}" # default to /output if variable not set

# Read topic name from environment variable, default to camera/image_raw
ROBOTO_PARAM_TOPIC="${ROBOTO_PARAM_TOPIC:-/camera/image_raw}"

# Check if the input directory exists
if [ ! -d "$ROBOTO_INPUT_DIR" ]; then
    echo "Input directory $ROBOTO_INPUT_DIR does not exist. Exiting."
    exit 1
fi

# Loop through each .bag file in the input directory
for bag_file in $ROBOTO_INPUT_DIR/*.bag; do
    # Check if the glob gets expanded to existing files.
    # If not, bag_file here will be exactly the string "$ROBOTO_INPUT_DIR/*.bag"
    # and the loop body will be skipped.
    [ -e "$bag_file" ] || continue

    # Extract the filename without the path and .bag extension
    bag_filename=$(basename -- "$bag_file")
    bag_name="${bag_filename%.*}"

    # Create an output directory for this bag file
    this_output_dir="$ROBOTO_OUTPUT_DIR/$bag_name"
    mkdir -p "$this_output_dir"

    # Execute roslaunch with the appropriate parameters
    roslaunch run_svo_slam.launch cam_name:=svo_test_pinhole input_rosbag:="$bag_file" output_directory:="$this_output_dir" topic_name:="$ROBOTO_PARAM_TOPIC"
done
