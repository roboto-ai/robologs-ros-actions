#!/bin/bash

BASE_DIR="./"

for SUBDIR in "$BASE_DIR"/*; do
  if [ -d "$SUBDIR" ]; then # Check if it is a directory
    echo "Processing directory: $SUBDIR"
    cd "$SUBDIR" # Change directory to the subdirectory
    
    # Check if the script exists and is executable
    if [ -x "./scripts/platform_test.sh" ]; then
      echo "Executing script in $SUBDIR"
      ./scripts/platform_test.sh
    else
      echo "Script not found or not executable in $SUBDIR"
    fi
    cd - > /dev/null # Go back to the previous directory
  fi
done
