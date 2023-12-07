import argparse
import os
import pathlib
import json

from roboto.domain import actions


def is_coco_format(file_path):
    """
    Check if the given file is in COCO format.

    Args:
    file_path (str): The path to the file.

    Returns:
    bool: True if the file is in COCO format, False otherwise.
    """
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
        return "images" in data and "annotations" in data and "categories" in data
    except json.JSONDecodeError:
        return False


def process_directory(input_dir, output_dir, output_file_name):
    """
    Process all JSON files in the given directory and its subdirectories,
    converting those in COCO format to Ultralytics format.

    Args:
    input_dir (pathlib.Path): The input directory containing JSON files.
    output_dir (pathlib.Path): The output directory to save converted files.
    output_file_name (str): The name of the output file.
    """
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                if is_coco_format(file_path):
                    with open(file_path, "r") as f:
                        coco_data = json.load(f)

                    ultralytics_data = convert_coco_to_ultralytics(coco_data)
                    relative_path = os.path.relpath(root, input_dir)
                    output_subdir = os.path.join(output_dir, relative_path)
                    os.makedirs(output_subdir, exist_ok=True)

                    output_file_path = os.path.join(output_subdir, output_file_name)
                    with open(output_file_path, "w") as f:
                        json.dump(ultralytics_data, f, indent=4)
                    print(f"Converted {file_path} to {output_file_path}")
                else:
                    print(f"Skipping {file_path} because it is not in COCO format")


def convert_coco_to_ultralytics(coco_data):
    """
    Convert COCO format data to Ultralytics format.

    Args:
    coco_data (dict): The COCO format data.

    Returns:
    dict: The Ultralytics format data.
    """
    ultralytics_format = {}
    output_dict = {}

    category_mapping = {
        category["id"]: category["name"] for category in coco_data["categories"]
    }
    image_size_mapping = {
        image["id"]: (image["width"], image["height"]) for image in coco_data["images"]
    }

    for image in coco_data["images"]:
        image_id = image["id"]
        file_name = image["file_name"]
        img_width, img_height = image_size_mapping[image_id]
        annotations = [
            ann for ann in coco_data["annotations"] if ann["image_id"] == image_id
        ]

        ultralytics_annotations = []
        for ann in annotations:
            category_name = category_mapping[ann["category_id"]]
            bbox = ann["bbox"]  # [x, y, width, height]
            segments = list()
            if len(ann["segmentation"]) > 0:
                segments = ann["segmentation"][0]

            ultralytics_bbox = {
                "x1": bbox[0] / img_width,
                "y1": bbox[1] / img_height,
                "x2": (bbox[0] + bbox[2]) / img_width,
                "y2": (bbox[1] + bbox[3]) / img_height,
            }
            if segments:
                ultralytics_segments = {
                    "x": [x / img_width for x in segments[0::2]],
                    "y": [y / img_height for y in segments[1::2]],
                }
            else:
                ultralytics_segments = {
                    "x": [],
                    "y": [],
                }

            ultralytics_annotation = {
                "name": category_name,
                "class": ann["category_id"],
                "confidence": 1.0,
                "box": ultralytics_bbox,
                "segments": ultralytics_segments,
            }
            ultralytics_annotations.append(ultralytics_annotation)

        ultralytics_format[file_name] = ultralytics_annotations

    output_dict["images"] = ultralytics_format
    output_dict["metadata"] = {}
    return output_dict


parser = argparse.ArgumentParser()
parser.add_argument(
    "-i",
    "--input-dir",
    dest="input_dir",
    type=pathlib.Path,
    required=False,
    help="Directory containing input files to process",
    default=os.environ.get(actions.InvocationEnvVar.InputDir.value),
)
parser.add_argument(
    "-o",
    "--output-dir",
    dest="output_dir",
    type=pathlib.Path,
    required=False,
    help="Directory to which to write any output files to be uploaded",
    default=os.environ.get(actions.InvocationEnvVar.OutputDir.value),
)

parser.add_argument(
    "-f",
    "--file-name",
    dest="file_name",
    type=str,
    required=False,
    default=os.environ.get("ROBOTO_PARAM_OUTPUT_FILE_NAME", "detections.json"),
    help="Output file name for converted COCO annotations",
)

args = parser.parse_args()
process_directory(args.input_dir, args.output_dir, args.file_name)
