#!/bin/bash

SCRIPTS_ROOT=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
PACKAGE_ROOT=$(dirname "${SCRIPTS_ROOT}")

# Define constants for directories and file paths

INPUT_DIR=${PACKAGE_ROOT}/test/input
ACTUAL_OUTPUT_DIR=${PACKAGE_ROOT}/test/actual_output
EXPECTED_OUTPUT_DIR=${PACKAGE_ROOT}/test/expected_output

if [ ! -d "$ACTUAL_OUTPUT_DIR" ]; then
    mkdir -p "$ACTUAL_OUTPUT_DIR"
fi

# Remove previous outputs
clean_actual_output() {
    rm -rf $ACTUAL_OUTPUT_DIR/
}

# Check if file exists
file_exists_or_error() {
    local file_path="$1"

    if [ ! -f "$file_path" ]; then
        echo "Error: File '$file_path' does not exist."
        exit 1
    fi
    echo "Test passed!"

}

# Run the docker command with the given parameters
run_docker_test() {
    local additional_args="$1"
    
    docker run \
        -v $INPUT_DIR:/input \
        -v $ACTUAL_OUTPUT_DIR:/output \
        -e ROBOTO_INPUT_DIR=/input \
        -e ROBOTO_OUTPUT_DIR=/output \
        $additional_args \
        get_images_from_video:latest
}

function check_file_does_not_exist() {
    local file_path="$1"
    if [[ ! -e "$file_path" ]]; then
        echo "Test passed!"
    else
        echo "Test failed: $1 exists!"
        exit 1
    fi
}

# Compare the actual output to the expected output
compare_outputs() {
    local actual_file="$1"
    local expected_file="$2"
    
    diff $ACTUAL_OUTPUT_DIR/$actual_file $EXPECTED_OUTPUT_DIR/$expected_file
    
    if [ $? -eq 0 ]; then
        echo "Test passed!"
    else
        echo "Test failed!"
	exit 1
    fi
}

# Main test execution
main() {

    # Test 1
    echo "Running Test 1: Test basic image extraction"
    clean_actual_output
    run_docker_test ""
    file_exists_or_error $ACTUAL_OUTPUT_DIR/avi/avi_frame_0000000.jpg
    file_exists_or_error $ACTUAL_OUTPUT_DIR/mkv/mkv_frame_0000000.jpg
    file_exists_or_error $ACTUAL_OUTPUT_DIR/mov/mov_frame_0000000.jpg
    file_exists_or_error $ACTUAL_OUTPUT_DIR/mp4/mp4_frame_0000000.jpg
   
}

# Run the main test execution
main
clean_actual_output
