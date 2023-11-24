#!/bin/bash

# Check if ROBOTO_OUTPUT_DIR is set
if [ -z "$ROBOTO_OUTPUT_DIR" ]; then
    echo "Error: ROBOTO_OUTPUT_DIR is not set."
    exit 1
fi

# Function to reindex and move a single .bag file while preserving the relative path
process_bag_file() {
    local file=$1
    echo "Reindexing $file"
    rosbag reindex "$file"

    # Construct the destination path
    local relative_path="${file#$ROBOTO_INPUT_DIR/}"
    local destination_dir="$ROBOTO_OUTPUT_DIR/$(dirname "$relative_path")"

    # Create the destination directory if it does not exist
    mkdir -p "$destination_dir"

    echo "Moving $file to $destination_dir"
    mv "$file" "$destination_dir"
}

# Export the function and include in subshell environments
export -f process_bag_file

# Check if ROBOTO_PARAM_FILE_PATH is set
if [ -n "$ROBOTO_PARAM_FILE_PATH" ]; then
    # Check if ROBOTO_INPUT_DIR is set
    if [ -z "$ROBOTO_INPUT_DIR" ]; then
        echo "Error: ROBOTO_INPUT_DIR is not set."
        exit 1
    fi

    # Construct full path from ROBOTO_INPUT_DIR and ROBOTO_PARAM_FILE_PATH
    full_path="$ROBOTO_INPUT_DIR/$ROBOTO_PARAM_FILE_PATH"

    # Check if the constructed full path is a valid .bag file
    if [ -f "$full_path" ] && [[ "$full_path" == *.bag ]]; then
        process_bag_file "$full_path"
    else
        echo "Error: The file specified in ROBOTO_PARAM_FILE_PATH does not exist or is not a .bag file."
        exit 1
    fi
else
    # Check if ROBOTO_INPUT_DIR is set
    if [ -z "$ROBOTO_INPUT_DIR" ]; then
        echo "Error: ROBOTO_INPUT_DIR is not set."
        exit 1
    fi

    # Process all .bag files in ROBOTO_INPUT_DIR and its subdirectories
    find "$ROBOTO_INPUT_DIR" -type f -name '*.bag' -exec bash -c '
        for file do
            process_bag_file "$file"
        done
    ' bash {} +
fi

echo "Script completed."

