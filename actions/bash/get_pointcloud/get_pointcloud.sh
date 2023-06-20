#!/bin/bash

source /opt/ros/noetic/setup.bash

# Check if enough arguments are given
if [ $# -ne 2 ]; then
    echo "Usage: $0 <input_dir> <output_dir>"
    exit 1
fi

# Check if the provided input argument is a directory
if [ ! -d "$1" ]; then
    echo "The first argument should be a directory"
    exit 1
fi

INPUT_DIR=$1
OUTPUT_DIR=$2

# Check and create output directory if it does not exist
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "Output directory does not exist. Creating..."
    mkdir -p $OUTPUT_DIR
fi

# Start roscore
roscore&

# Iterate over .bag files in the input directory
for bagfile in $INPUT_DIR/*.bag; do
    # Get filename without extension
    filename=$(basename -- "$bagfile")
    filename="${filename%.*}"
    
    # Create subdirectory in the output directory using filename
    mkdir -p $OUTPUT_DIR/$filename
    
    # Run the pointcloud extraction script
    rosrun pcl_ros bag_to_pcd $bagfile /hesai/pandar $OUTPUT_DIR/$filename
done