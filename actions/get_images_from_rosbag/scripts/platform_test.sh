#!/bin/bash

ACTION_NAME=get_images_from_rosbag
INPUT_FILE_PATH="./test/input/tiny.bag"
EXPECTED_OUTPUT_FILE_NAME="dvs_image_raw_000000.jpg"
INPUT_DATA="*bag"
ORG=${ORG}

# Check for command line argument for ORG, fallback to roboto-public if not provided
if [ -z "$1" ]; then
  ORG="roboto-public"
else
  ORG=$1
fi

# Step 1: Build and deploy docker image
./scripts/build.sh
./scripts/setup.sh
./scripts/deploy.sh "$ORG"

# Step 2: Create dataset on platform and parse its ID
create_output=$(roboto datasets create --org "$ORG")
dataset_id=$(echo "$create_output" | jq -r '.dataset_id')

if [ -z "$dataset_id" ]; then
  echo "Failed to create dataset"
  exit 1
fi

echo "Dataset created with ID: $dataset_id"

# Step 3: Upload a test file to the dataset
roboto datasets upload-files -d "$dataset_id" -p "$INPUT_FILE_PATH"

# Step 4: Invoke the Action and parse Invocation ID
invoke_output=$(roboto actions invoke "$ACTION_NAME" --dataset-id "$dataset_id" --input-data "$INPUT_DATA" --org "$ORG")
invocation_id=$(echo "$invoke_output" | grep -oP "Invocation ID: '\K[^']+" )

if [ -z "$invocation_id" ]; then
  echo "Failed to invoke action"
  exit 1
fi

echo "Action invoked with ID: $invocation_id"

# Step 5: Monitor the invocation status
end_time=$(date -ud "5 minutes" +%s)
while true; do
  now=$(date +%s)
  if (( now > end_time )); then
    echo "Invocation monitoring timed out for $ACTION_NAME"
    exit 1
  fi

  status_output=$(roboto invocations status "$invocation_id")
  status=$(echo "$status_output" | jq -r '.[-1].status')

  case $status in
    "Completed")
      echo "Action completed"
      break
      ;;
    "Failed")
      echo "Action failed for $ACTION_NAME"
      roboto invocations logs $invocation_id
      exit 1
      ;;
    *)
      echo "Current status: $status. Checking again in 20 seconds..."
      sleep 20
      ;;
  esac
done

# Step 6: Verify the output files
list_output=$(roboto datasets list-files -d "$dataset_id")
if echo "$list_output" | grep -q "$EXPECTED_OUTPUT_FILE_NAME"; then
  echo "Test succeeded for $ACTION_NAME"
else
  echo "Test failed for $ACTION_NAME"
fi

