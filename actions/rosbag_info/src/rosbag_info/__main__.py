import argparse
import math
import os
import pathlib
import os.path
import json
from bagpy import bagreader
from typing import Union

from roboto.domain import actions


def get_bag_info_from_file_or_folder(input_path: str) -> dict:
    """
    Recursively search for rosbag files in the given path and return their metadata.

    Args:
        input_path (str): Input file path of a rosbag or a directory.

    Returns:
        dict: Metadata of each rosbag found. The key is the rosbag's absolute file path.
    """
    rosbag_info_dict = dict()

    if str(input_path).endswith(".bag"):
        rosbag_info_dict[os.path.abspath(input_path)] = get_bag_info_from_file(
            input_path
        )
    else:
        for root, _, files in os.walk(input_path):
            for filename in files:
                if filename.endswith(".bag"):
                    full_path = os.path.join(root, filename)
                    rosbag_info_dict[
                        os.path.abspath(full_path)
                    ] = get_bag_info_from_file(full_path)

    return rosbag_info_dict


def convert_nan_values_to_string(input_dict: dict) -> dict:
    """
    Convert all values of a dictionary to string.
    Args:
        input_dict (dict): dict to convert

    Returns: dict with values as strings

    """
    if "Frequency" in input_dict:
        if math.isnan(input_dict["Frequency"]):
            input_dict["Frequency"] = "NaN"
    return input_dict


def get_bag_info_from_file(rosbag_path: str) -> dict:
    """
    Get metadata of a specified rosbag.

    Args:
        rosbag_path (str): Input file path of the rosbag.

    Returns:
        dict: Metadata of the rosbag.
    """
    if not os.path.exists(rosbag_path):
        raise FileNotFoundError(f"{rosbag_path} does not exist.")

    if not rosbag_path.endswith(".bag"):
        raise ValueError(f"{rosbag_path} is not a rosbag.")

    try:
        bag = bagreader(rosbag_path, tmp=True)
    except Exception as e:
        print(f"Couldn't open rosbag {rosbag_path} due to error: {e}. Skipping...")
        return dict()

    file_stats = os.stat(rosbag_path)

    topic_metadata_list = bag.topic_table.to_dict("records")

    for it, entry in enumerate(topic_metadata_list):
        topic_metadata_list[it] = convert_nan_values_to_string(entry)

    return {
        "file_name": os.path.split(rosbag_path)[1],
        "start_time": bag.start_time,
        "end_time": bag.end_time,
        "duration": bag.end_time - bag.start_time,
        "file_size_mb": str(file_stats.st_size / (1024 * 1024)),
        "topics": topic_metadata_list,
    }


def save_json(data: Union[dict, list], path: str) -> None:
    """
    Save data as a JSON file.

    Args:
        data (Union[dict, list]): Data to be saved.
        path (str): Output file path.
    """
    with open(path, "w") as f_json:
        json.dump(data, f_json, indent=4, sort_keys=True)


def main(args: argparse.Namespace) -> None:
    """
    Get summary of Rosbag1 data based on the provided arguments.

    Args:
        args (argparse.Namespace): Parsed command line arguments.
    """
    input_path = args.input_dir
    output_path = args.output_dir

    rosbag_info_dict = get_bag_info_from_file_or_folder(input_path=input_path)

    if not args.file_name:
        args.file_name = "rosbag_metadata.json"

    output_filename = args.file_name if not args.hidden else "." + args.file_name

    if args.split:
        for bag_path, bag_info in rosbag_info_dict.items():
            bag_dir = os.path.dirname(bag_path)
            bag_name = os.path.basename(bag_path) + ".json"
            if args.hidden:
                bag_name = "." + bag_name

            if args.output_dir:
                # Calculate the relative path of the rosbag to the input directory
                relative_path = os.path.relpath(bag_dir, input_path)

                # Create the same folder structure in the output directory
                output_dir = os.path.join(output_path, relative_path)
                os.makedirs(output_dir, exist_ok=True)

                output_file_path = os.path.join(output_dir, bag_name)
            else:
                output_file_path = os.path.join(bag_dir, bag_name)

            save_json(data=bag_info, path=output_file_path)
    else:
        if os.path.isdir(output_path):
            output_file_path = os.path.join(output_path, output_filename)
        elif os.path.isfile(output_path):
            output_file_path = output_path
        else:
            raise ValueError("Invalid output path provided.")

        save_json(data=rosbag_info_dict, path=output_file_path)

    return


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
    "-s",
    "--split",
    action="store_true",
    required=False,
    help="Save individual metadata files next to each rosbag",
    default=(os.environ.get("ROBOTO_PARAM_SPLIT") == "True"),
)

parser.add_argument(
    "-f",
    "--file-name",
    type=str,
    required=False,
    default=os.environ.get("ROBOTO_PARAM_FILE_NAME"),
    help="Output file name. Only relevant if --split is not used",
)

parser.add_argument(
    "-d",
    "--hidden",
    action="store_true",
    required=False,
    help="Output hidden JSON files with '.' prefix",
    default=(os.environ.get("ROBOTO_PARAM_HIDDEN") == "True"),
)

args = parser.parse_args()
main(args)
