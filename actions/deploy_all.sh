#!/bin/bash

# Define the list of directories
DIRECTORIES=(
    "get_images_from_rosbag"
    "get_videos_from_rosbag"
    "parse_rosout_and_tag"
    "rosbag_to_csv"
    "rosbag_to_mcap"
    "run_yolov8_rosbag"
    "run_svo_slam_rosbag"
    "avi_to_mp4"
    "convert_coco_annotations"
    "get_images_from_video"
    "merge_rosbags"
    "rosbag_reindex"
)

# Function to execute commands in a directory
execute_commands() {
    local dir=$1

    echo "Processing directory: $dir"

    # Check if the directory exists
    if [[ -d "$dir" ]]; then
        # Change to directory
        cd "$dir"

        # Check if the scripts exist and are executable
        if [[ -x "scripts/setup.sh" ]] && [[ -x "scripts/deploy.sh" ]]; then
            echo "Running setup script..."
            ./scripts/setup.sh

            echo "Running deploy script..."
            ./scripts/deploy.sh roboto-public
        else
            echo "Error: Required scripts not found or not executable in $dir"
        fi

        # Change back to the parent directory
        cd ..
    else
        echo "Error: Directory $dir does not exist"
    fi

    echo "Finished processing directory: $dir"
    echo "--------------------------------------"
}

# Iterate over the directories and execute the commands
for dir in "${DIRECTORIES[@]}"; do
    execute_commands "$dir"
done

echo "All directories processed."
