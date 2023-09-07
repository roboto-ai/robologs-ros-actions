#!/bin/bash

# Function to check if a directory is set and exists
check_directory_exists() {
    if [ -z "$1" ]; then
        return 1
    fi

    if [ ! -d "$1" ]; then
        return 2
    fi

    return 0
}

# Get input and output directories from arguments or environment variables
input_directory=${1:-$ROBOTO_INPUT_DIR}
output_directory=${2:-$ROBOTO_OUTPUT_DIR}

# Check if the right number of arguments are given or if environment variables are set
if ! check_directory_exists "$input_directory"; then
    if [ -z "$1" ] && [ "$?" -eq 1 ]; then
        echo "No input directory argument given and ROBOTO_INPUT_DIR is not set"
        exit 1
    fi
    echo "Input directory does not exist"
    exit 1
fi

# Check if the output directory exists, if not create it
if ! check_directory_exists "$output_directory"; then
    if [ -z "$2" ] && [ "$?" -eq 1 ]; then
        echo "No output directory argument given and ROBOTO_OUTPUT_DIR is not set"
        exit 1
    fi
    mkdir -p "$output_directory"
fi

# Loop over .bag files in the input directory and its subdirectories
find "$input_directory" -type f -name "*.bag" | while read -r bag_file
do
    # Get the base name of the bag file
    base_name=$(basename "$bag_file" .bag)

    # Run the conversion command
    echo "Converting $bag_file to $base_name.mcap"
    mcap convert "$bag_file" "$output_directory/$base_name.mcap"
done
