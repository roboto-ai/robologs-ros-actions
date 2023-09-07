#!/bin/bash

source /opt/ros/noetic/setup.bash
source /function/svo_ws/devel/setup.bash

# Execute commands passed to docker run
exec "$@"
