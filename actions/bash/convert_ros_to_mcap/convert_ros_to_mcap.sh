#!/bin/bash

# Check if the right number of arguments are given
if [ $# -ne 2 ]
then
    echo "Usage: ./script.sh <input_directory> <output_directory>"
    exit 1
fi

input_directory=$1
output_directory=$2

# Check if the input directory exists
if [ ! -d "$input_directory" ]
then
    echo "Input directory does not exist"
    exit 1
fi

# Check if the output directory exists, if not create it
if [ ! -d "$output_directory" ]
then
    mkdir -p "$output_directory"
fi

# Loop over .bag files in the input directory
for bag_file in "$input_directory"/*.bag
do
    # Get the base name of the bag file
    base_name=$(basename "$bag_file" .bag)

    # Run the conversion command
    mcap convert "$bag_file" "$output_directory/$base_name.mcap"
done
