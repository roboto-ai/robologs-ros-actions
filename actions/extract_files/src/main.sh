#!/bin/bash

# Ensure input and output directories are provided
if [[ -z "$ROBOTO_INPUT_DIR" || -z "$ROBOTO_OUTPUT_DIR" ]]; then
    echo "Error: Input and output directories must be set."
    exit 1
fi

# Process each zip file
find "$ROBOTO_INPUT_DIR" -type f -name "*.zip" | while read -r file; do
    base_name=$(basename "$file" .zip)
    if [[ "$ROBOTO_PARAM_ISOLATE_EXTRACTION" == "True" ]]; then
        mkdir -p "$ROBOTO_OUTPUT_DIR/$base_name"
        unzip -o "$file" -d "$ROBOTO_OUTPUT_DIR/$base_name"
    else
        unzip -o "$file" -d "$ROBOTO_OUTPUT_DIR"
    fi
done

# Process each tar file
find "$ROBOTO_INPUT_DIR" -type f -name "*.tar" | while read -r file; do
    base_name=$(basename "$file" .tar)
    if [[ "$ROBOTO_PARAM_ISOLATE_EXTRACTION" == "True" ]]; then
        mkdir -p "$ROBOTO_OUTPUT_DIR/$base_name"
        tar -xvf "$file" -C "$ROBOTO_OUTPUT_DIR/$base_name"
    else
        tar -xvf "$file" -C "$ROBOTO_OUTPUT_DIR"
    fi
done

# Process each tar.gz file
find "$ROBOTO_INPUT_DIR" -type f -name "*.tar.gz" | while read -r file; do
    base_name=$(basename "$file" .tar.gz)
    if [[ "$ROBOTO_PARAM_ISOLATE_EXTRACTION" == "True" ]]; then
        mkdir -p "$ROBOTO_OUTPUT_DIR/$base_name"
        tar -xzvf "$file" -C "$ROBOTO_OUTPUT_DIR/$base_name"
    else
        tar -xzvf "$file" -C "$ROBOTO_OUTPUT_DIR"
    fi
done

echo "Extraction complete."

