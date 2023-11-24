#!/usr/bin/env bash

set -euo pipefail

SCRIPTS_ROOT=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
PACKAGE_ROOT=$(dirname "${SCRIPTS_ROOT}")

# Early exit if virtual environment does not exist and/or roboto is not yet installed
if [ ! -f "$PACKAGE_ROOT/.venv/bin/roboto" ]; then
    echo "Virtual environment with roboto CLI does not exist. Please run ./scripts/setup.sh first."
    exit 1
fi

# Set org_id to $ROBOTO_ORG_ID if defined, else the first argument passed to this script
org_id=${ROBOTO_ORG_ID:-}
if [ $# -gt 0 ]; then
    org_id=$1  
fi

roboto_exe="$PACKAGE_ROOT/.venv/bin/roboto"

echo "Pushing rosbag_reindex:latest to Roboto's private registry"
image_push_args=(
    --suppress-upgrade-check
    images push
    --quiet
)
if [[ -n $org_id ]]; then
    image_push_args+=(--org $org_id)
fi
image_push_args+=(rosbag_reindex:latest)
image_push_ret_code=0
image_uri=$($roboto_exe "${image_push_args[@]}")
image_push_ret_code=$?

if [ $image_push_ret_code -ne 0 ]; then
    echo "Failed to push rosbag_reindex:latest to Roboto's private registry"
    exit 1
fi

echo "Creating rosbag_reindex action"
create_args=(
  --from-file $PACKAGE_ROOT/action.json
  --image $image_uri
  --yes
)
if [[ -n $org_id ]]; then
    create_args+=(--org $org_id)
fi
$roboto_exe actions create "${create_args[@]}"
