#!/bin/bash
set -euo pipefail

# Ensure input and output directories are provided
if [[ -z "${ROBOTO_INPUT_DIR:-}" || -z "${ROBOTO_OUTPUT_DIR:-}" ]]; then
    echo "Error: ROBOTO_INPUT_DIR and ROBOTO_OUTPUT_DIR must be set." >&2
    exit 1
fi

# Create output directory path based on input file and settings
create_output_dir() {
    local file="$1"
    local relative_path="${file#$ROBOTO_INPUT_DIR/}"
    local base_name=$(basename "$file")
    local dir_name=$(dirname "$relative_path")
    local output_dir="$ROBOTO_OUTPUT_DIR/$dir_name"

    if [[ "${ROBOTO_PARAM_ISOLATE_EXTRACTION:-}" == "True" ]]; then
        local base_name_no_ext="${base_name%%.*}" # removes multiple extensions like .tar.gz
        output_dir="$output_dir/${base_name_no_ext}_dir"
    fi

    mkdir -p "$output_dir"
    echo "$output_dir"
}

# Find supported archive files
mapfile -t archive_files < <(find "$ROBOTO_INPUT_DIR" -type f \( -name "*.zip" -o -name "*.tar" -o -name "*.tar.gz" -o -name "*.tgz" -o -name "*.tar.xz" \))

# Fail and exit if no archives are found
if [[ ${#archive_files[@]} -eq 0 ]]; then
    echo "Error: No supported archive files found in \$ROBOTO_INPUT_DIR ($ROBOTO_INPUT_DIR)" >&2
    exit 1
fi

# Process each archive
for file in "${archive_files[@]}"; do
    output_dir=$(create_output_dir "$file")

    echo "Extracting: $file -> $output_dir"

    case "$file" in
    *.zip)
        unzip -o "$file" -d "$output_dir" || {
            echo "Failed to unzip $file" >&2
            exit 1
        }
        ;;
    *.tar)
        tar -xvf "$file" -C "$output_dir" || {
            echo "Failed to extract $file" >&2
            exit 1
        }
        ;;
    *.tar.gz | *.tgz)
        tar -xzvf "$file" -C "$output_dir" || {
            echo "Failed to extract $file" >&2
            exit 1
        }
        ;;
    *.tar.xz)
        tar -xJvf "$file" -C "$output_dir" || {
            echo "Failed to extract $file" >&2
            exit 1
        }
        ;;
    *)
        echo "Unsupported file type: $file" >&2
        exit 1
        ;;
    esac
done

echo "Extraction complete."
