#!/bin/sh

set -e

echo "Hello, Roboto!"
echo "This Action's input directory is $ROBOTO_INPUT_DIR"
echo "This Action's output directory is $ROBOTO_OUTPUT_DIR"
echo "Here are all available environment variables:"
env -0 | sort -z | tr '\0' '\n'
