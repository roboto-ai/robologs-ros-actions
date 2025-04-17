#!/bin/bash

# Ensure input and output directories are provided
if [[ -z "$ROBOTO_INPUT_DIR" || -z "$ROBOTO_OUTPUT_DIR" ]]; then
    echo "Error: Input and output directories must be set."
    exit 1
fi

# Function to create output directory preserving the original path
create_output_dir() {
    local file="$1"
    local output_dir="$ROBOTO_OUTPUT_DIR"
    local relative_path="${file#$ROBOTO_INPUT_DIR/}"
    local base_name=$(basename "$file")
    local dir_name=$(dirname "$relative_path")

    if [[ "$ROBOTO_PARAM_ISOLATE_EXTRACTION" == "True" ]]; then
        # Strip the extension and append _dir
        local base_name_no_ext="${base_name%.*}"
        output_dir="$output_dir/$dir_name/${base_name_no_ext}"
    else
        output_dir="$output_dir/$dir_name"
    fi

    mkdir -p "$output_dir"
    echo "$output_dir"
}

# Process each zip file
find "$ROBOTO_INPUT_DIR" -type f -name "*.zip" | while read -r file; do
    output_dir=$(create_output_dir "$file")
    unzip -o "$file" -d "$output_dir"
done

# Process each tar file
find "$ROBOTO_INPUT_DIR" -type f -name "*.tar" | while read -r file; do
    output_dir=$(create_output_dir "$file")
    tar -xvf "$file" -C "$output_dir"
done

# Process each tar.gz file
find "$ROBOTO_INPUT_DIR" -type f -name "*.tar.gz" | while read -r file; do
    output_dir=$(create_output_dir "$file")
    tar -xzvf "$file" -C "$output_dir"
done

echo "Extraction complete."

