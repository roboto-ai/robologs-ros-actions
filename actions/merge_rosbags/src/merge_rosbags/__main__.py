import argparse
import os
import pathlib
import glob
from . import bag_stream

from roboto.domain import actions


def find_bag_files(directory):
    """
    Finds all files with the .bag extension in the specified directory.

    :param directory: Path of the directory to search in.
    :return: List of file paths ending with .bag. Returns an empty list if no such files are found.
    """
    # Construct the search pattern
    search_pattern = os.path.join(directory, "*.bag")

    # Find all files with .bag extension
    bag_files = glob.glob(search_pattern)

    return bag_files


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
    "--topics",
    type=str,
    required=False,
    help="Comma-separated list of topics to be merged. If empty, all topics are merged",
    default=os.environ.get("ROBOTO_PARAM_TOPICS"),
)

parser.add_argument(
    "--output_file_name",
    type=str,
    required=False,
    help="Output bag name with merged topics",
    default=os.environ.get("ROBOTO_PARAM_OUTPUT_FILE_NAME", "merged.bag"),
)

parser.add_argument(
    "--output_folder_name",
    type=str,
    required=False,
    help="Output folder path of merged bag file",
    default=os.environ.get("ROBOTO_PARAM_OUTPUT_FOLDER_NAME"),
)

args = parser.parse_args()

input_bags = find_bag_files(args.input_dir)

topics = args.topics
topics_list = args.topics.replace(" ", "").split(",") if args.topics else []

if args.output_folder_name:
    output_path = os.path.join(args.output_dir, args.output_folder_name)

else:
    output_path = args.output_dir

if not os.path.exists(output_path):
    os.makedirs(output_path)

bag_stream.main(input_bags, topics_list, output_path, args.output_file_name, True)
