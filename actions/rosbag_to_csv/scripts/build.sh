#!/usr/bin/env bash

set -euo pipefail

SCRIPTS_ROOT=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
PACKAGE_ROOT=$(dirname "${SCRIPTS_ROOT}")

build_subcommand=(build)
# if buildx is installed, use it
if docker buildx version &> /dev/null; then
    build_subcommand=(buildx build --platform linux/amd64 --output type=image)
fi

docker "${build_subcommand[@]}" -f $PACKAGE_ROOT/Dockerfile -t rosbag_to_csv:latest $PACKAGE_ROOT
