#!/usr/bin/env bash

set -euo pipefail

SCRIPTS_ROOT=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
PACKAGE_ROOT=$(dirname "${SCRIPTS_ROOT}")

# Set input_dir to $ROBOTO_INPUT_DIR if defined, else the first argument passed to this script
input_dir=${ROBOTO_INPUT_DIR:-}
if [ $# -gt 0 ]; then
    input_dir=$1  
fi

# Fail if input_dir is not an existing directory
if [ ! -d "$input_dir" ]; then
    echo "Specify an existing input directory as the first argument to this script, or set the ROBOTO_INPUT_DIR environment variable"
    exit 1
fi

# Set output_dir variable to $ROBOTO_OUTPUT_DIR if defined, else set it to "output/" in the package root (creating if necessary)
output_dir=${ROBOTO_OUTPUT_DIR:-$PACKAGE_ROOT/output}
mkdir -p $output_dir

# Assert both directories are absolute paths
if [[ ! "$input_dir" = /* ]]; then
    echo "Input directory '$input_dir' must be specified as an absolute path"
    exit 1
fi

if [[ ! "$output_dir" = /* ]]; then
    echo "Output directory '$output_dir' must be specified as an absolute path"
    exit 1
fi

docker run --rm -it \
    -v $input_dir:/input \
    -v $output_dir:/output \
    -e ROBOTO_INPUT_DIR=/input \
    -e ROBOTO_OUTPUT_DIR=/output \
    avi_to_mp4:latest
