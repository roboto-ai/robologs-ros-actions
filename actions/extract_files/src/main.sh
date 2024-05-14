#!/bin/sh

# Ensure input and output directories are provided
if [[ -z "$ROBOTO_INPUT_DIR" || -z "$ROBOTO_OUTPUT_DIR" ]]; then
    echo "Error: Input and output directories must be set."
    exit 1
fi

# Process each zip file
for file in "$ROBOTO_INPUT_DIR"/*.zip; do
    if [[ -f "$file" ]]; then
        base_name=$(basename "$file" .zip)
        if [[ "$ROBOTO_PARAM_ISOLATE_EXTRACTION" == "True" ]]; then
            mkdir -p "$ROBOTO_OUTPUT_DIR/$base_name"
            unzip -o "$file" -d "$ROBOTO_OUTPUT_DIR/$base_name"
        else
            unzip -o "$file" -d "$ROBOTO_OUTPUT_DIR"
        fi
    fi
done

# Process each tar file
for file in "$ROBOTO_INPUT_DIR"/*.tar; do
    if [[ -f "$file" ]]; then
        base_name=$(basename "$file" .tar)
        if [[ "$ROBOTO_PARAM_ISOLATE_EXTRACTION" == "True" ]]; then
            mkdir -p "$ROBOTO_OUTPUT_DIR/$base_name"
            tar -xvf "$file" -C "$ROBOTO_OUTPUT_DIR/$base_name"
        else
            tar -xvf "$file" -C "$ROBOTO_OUTPUT_DIR"
        fi
    fi
done

# Process each tar.gz file
for file in "$ROBOTO_INPUT_DIR"/*.tar.gz; do
    if [[ -f "$file" ]]; then
        base_name=$(basename "$file" .tar.gz)
        if [[ "$ROBOTO_PARAM_ISOLATE_EXTRACTION" == "True" ]]; then
            mkdir -p "$ROBOTO_OUTPUT_DIR/$base_name"
            tar -xzvf "$file" -C "$ROBOTO_OUTPUT_DIR/$base_name"
        else
            tar -xzvf "$file" -C "$ROBOTO_OUTPUT_DIR"
        fi
    fi
done

echo "Extraction complete."
