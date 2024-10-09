#!/bin/bash

# Check if ROBOTO_OUTPUT_DIR is set
if [ -z "$ROBOTO_OUTPUT_DIR" ]; then
    echo "Error: ROBOTO_OUTPUT_DIR is not set."
    exit 1
fi

# Function to reindex a .bag.active file, rename it by removing .active, and move it while preserving the relative path
process_bag_active_file() {
    local file=$1
    local base_name="${file%.bag.active}"
    local renamed_file="${base_name}.bag"

    echo "Reindexing $file"
    rosbag reindex "$file"

    # Construct the destination path
    local relative_path="${file#$ROBOTO_INPUT_DIR/}"
    local destination_dir="$ROBOTO_OUTPUT_DIR/$(dirname "$relative_path")"

    # Create the destination directory if it does not exist
    mkdir -p "$destination_dir"

    # Rename the file by removing the .active extension
    echo "Renaming $file to $renamed_file"
    mv "$file" "$renamed_file"

    # Move the renamed file to the destination directory
    echo "Moving $renamed_file to $destination_dir"
    mv "$renamed_file" "$destination_dir"
}

# Export the function and include in subshell environments
export -f process_bag_active_file

# Check if ROBOTO_INPUT_DIR is set
if [ -z "$ROBOTO_INPUT_DIR" ]; then
    echo "Error: ROBOTO_INPUT_DIR is not set."
    exit 1
fi

# Process all .bag.active files in ROBOTO_INPUT_DIR and its subdirectories
find "$ROBOTO_INPUT_DIR" -type f -name '*.bag.active' -exec bash -c '
    for file do
        process_bag_active_file "$file"
    done
' bash {} +

echo "Script completed."
