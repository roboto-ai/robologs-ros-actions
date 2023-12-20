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
        run_yolov8_rosbag:latest
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
    file_exists_or_error $ACTUAL_OUTPUT_DIR/tiny/dvs_image_raw/imgs/dvs_image_raw_000000.jpg
    # Check second
    file_exists_or_error $ACTUAL_OUTPUT_DIR/tiny/dvs1_image_raw/imgs/dvs1_image_raw_000002.jpg
   
    # Test 2
    echo "Running Test 2: Verify different file formats"
    clean_actual_output
    run_docker_test "-e ROBOTO_PARAM_FORMAT=png"
    file_exists_or_error $ACTUAL_OUTPUT_DIR/tiny/dvs_image_raw/imgs/dvs_image_raw_000000.png

    # Test 3
    echo "Running Test 3: Verify msg_timestamp output naming"
    clean_actual_output
    run_docker_test "-e ROBOTO_PARAM_NAMING=msg_timestamp"
    file_exists_or_error $ACTUAL_OUTPUT_DIR/tiny/dvs_image_raw/imgs/dvs_image_raw_1540820324517214132.jpg
    
    #clean_actual_output
    run_docker_test "-e ROBOTO_PARAM_NAMING=rosbag_timestamp"
    file_exists_or_error $ACTUAL_OUTPUT_DIR/tiny/dvs_image_raw/imgs/dvs_image_raw_1696854171077412542.jpg

    # Test 4
    echo "Running Test 4: Verify sampling"
    clean_actual_output
    run_docker_test "-e ROBOTO_PARAM_SAMPLE=2"
    check_file_does_not_exist $ACTUAL_OUTPUT_DIR/tiny/dvs_image_raw/imgs/dvs_image_raw_000001.jpg

    # Test 5
    echo "Running Test 5: Verify start, end time trimming"
    clean_actual_output
    run_docker_test "-e ROBOTO_PARAM_END_TIME=0.05"
    check_file_does_not_exist $ACTUAL_OUTPUT_DIR/tiny/dvs_image_raw/imgs/dvs_image_raw_000003.jpg
    clean_actual_output
    run_docker_test "-e ROBOTO_PARAM_START_TIME=0.05"
    check_file_does_not_exist $ACTUAL_OUTPUT_DIR/tiny/dvs_image_raw/imgs/dvs_image_raw_000000.jpg

    # Test 6
    echo "Running Test 6: Verify detections"
    clean_actual_output
    run_docker_test "-e ROBOTO_PARAM_TOPICS=/dvs/image_raw"
    file_exists_or_error $ACTUAL_OUTPUT_DIR/tiny/dvs_image_raw/imgs/detections.json
    file_exists_or_error $ACTUAL_OUTPUT_DIR/tiny/dvs_image_raw/imgs/img_manifest.json
    #run_docker_test "-e ROBOTO_PARAM_SAVE_VIDEO=True"
    #file_exists_or_error $ACTUAL_OUTPUT_DIR/tiny/dvs_image_raw/video.mp4

    # Test 7
    echo "Running Test 6: Verify output video"
    clean_actual_output
    run_docker_test "-e ROBOTO_PARAM_TOPICS=/dvs/image_raw -e ROBOTO_PARAM_SAVE_VIDEO=True"
    file_exists_or_error $ACTUAL_OUTPUT_DIR/tiny/dvs_image_raw/video.mp4

}

# Run the main test execution
main
clean_actual_output
