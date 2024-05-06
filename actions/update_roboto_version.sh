#!/bin/bash

# Check if a version number is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <new-version>"
    exit 1
fi

# The new version number to replace with
new_version=$1

# Find all 'requirements.runtime.txt' files and update them
find . -type f -name 'requirements.runtime.txt' -exec sed -i "s/roboto==[0-9]*\.[0-9]*\.[0-9]*/roboto==$new_version/g" {} +

echo "All 'requirements.runtime.txt' files have been updated with roboto==$new_version."

