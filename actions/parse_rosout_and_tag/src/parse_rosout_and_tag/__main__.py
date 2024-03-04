import argparse
import os
import json
import sys
import pandas as pd
import logging
import glob
import ast

from typing import List
from bagpy import bagreader
from roboto.domain import actions
from roboto.env import RobotoEnvKey

# Setting up the logger
logger = logging.getLogger("test-user-defined-action")
logging.root.handlers = []
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)4s:%(filename)s %(lineno)4s %(asctime)s] %(message)s",
    handlers=[logging.StreamHandler()],  # log to stderr
)


def get_all_files_of_type_in_directory(input_folder: str, file_format: str) -> list:
    """
    This function gets a list of all files of type "file_format" in a directory
    Args:
        input_folder (str): input folder path

    Returns: list with files of certain type

    """

    subfolder_list = list_all_subfolders(input_folder)

    file_string = f"./*.{file_format}"
    ll = list()
    # look for files in subfolders
    print(subfolder_list)
    for entry in subfolder_list:
        ll = ll + sorted(glob.glob(os.path.abspath(os.path.join(entry, file_string))))

    # look for files in folder
    ll = ll + sorted(
        glob.glob(os.path.abspath(os.path.join(input_folder, file_string)))
    )
    return ll


def list_all_subfolders(folder_path: str) -> list:
    """
    This function lists all subfolders in a folder
    Args:
        folder_path ():

    Returns:

    """
    subfolders = []

    for root, dirs, files in os.walk(folder_path):
        for directory in dirs:
            subfolder_path = os.path.join(root, directory)
            subfolders.append(subfolder_path)

    return subfolders


def convert_to_dict(dict_string: str) -> dict:
    """
    Convert a string to a dictionary.

    Args:
        dict_string: A string representation of a dictionary.

    Returns:
        The converted dictionary.

    Raises:
        argparse.ArgumentTypeError: If the string cannot be safely evaluated to a dictionary.
    """
    try:
        return ast.literal_eval(
            dict_string
        )  # Safely parse a string to a Python literal
    except ValueError:
        raise argparse.ArgumentTypeError("Dictionary expected")


def save_dataset_md_changeset_json(
    add_tag_list: List[str], remove_tag_list: List[str], output_path: str
) -> None:
    """
    This function creates a changeset JSON for the dataset and save it to the output path.

    Args:
        add_tag_list (List[str]): A list of tags to add to the robot run.
        remove_tag_list (List[str]): A list of tags to remove from the robot run.
        output_path (str): The path to save the changeset JSON.

    Returns:
        None
    """
    changeset_json = dict()
    changeset_json["put_tags"] = add_tag_list
    changeset_json["remove_tags"] = remove_tag_list

    with open(output_path, "w") as output_path:
        json.dump(changeset_json, output_path)

    return


def save_tags(tag_list: List[str]) -> None:
    # Save changeset JSON
    output_path_changeset = os.getenv(
        "ROBOTO_DATASET_METADATA_CHANGESET_FILE", "/output/changeset.json"
    )
    save_dataset_md_changeset_json(
        add_tag_list=tag_list, output_path=output_path_changeset, remove_tag_list=[]
    )

    return


def main(args):
    """
    Main function that sets up command line arguments, checks environment variables,
    and calls the main processing function.
    """

    if args.input_dir is None:
        logger.error("Missing required input directory.")
        sys.exit(1)

    if args.output_dir is None:
        logger.error("Missing required output directory.")
        sys.exit(1)

    print(f"The dictionary is: {args.dictionary}")

    check_for_errors_in_logs(input_dir=args.input_dir, keyword_dict=args.dictionary)


def check_for_errors_in_logs(input_dir: str, keyword_dict: dict) -> None:
    """
    This function checks ROS bag files in a specified directory for specific log
    strings and saves a tag if such a string is encountered.

    Args:
        input_dir: The input directory where ROS bag files are located.
        keyword_dict: A dictionary of keywords to search for in the /rosout logs.

    Returns:
        None
    """
    # Get all the bag files in the input directory
    bag_files = get_all_files_of_type_in_directory(
        input_folder=input_dir, file_format="bag"
    )

    # Logging the bag files that are going to be checked
    logger.info(f"Checking the following bag files: {bag_files}")

    tags = list()

    # Iterate over each bag file
    for bag_file in bag_files:
        try:
            bag = bagreader(bag_file)
            topics = bag.topic_table["Topics"].tolist()
            # If the "/rosout" topic exists in the bag file, check for error log string
            if "/rosout" in topics:
                data = bag.message_by_topic("/rosout")
                df = pd.read_csv(data)
                print(df["msg"])

                for k in keyword_dict.keys():
                    if df["msg"].str.contains(keyword_dict[k]).any():
                        if k not in tags:
                            tags.append(k)

        except Exception as e:
            # Logging the exception encountered and the file causing it
            logger.error(f"Couldn't read rosbag: {bag_file}. Error: {e}")
            continue

    # Save tags
    save_tags(tag_list=tags)


parser = argparse.ArgumentParser()
parser.add_argument(
    "-i",
    "--input-dir",
    dest="input_dir",
    type=str,
    required=False,
    help="Directory containing input files to process",
    default=os.environ.get(RobotoEnvKey.InputDir.value),
)
parser.add_argument(
    "-o",
    "--output-dir",
    dest="output_dir",
    type=str,
    required=False,
    help="Directory to which to write any output files to be uploaded",
    default=os.environ.get(RobotoEnvKey.OutputDir.value),
)

parser.add_argument(
    "-d",
    "--dictionary",
    type=convert_to_dict,
    default=os.getenv("ROBOTO_PARAM_KEYWORD_DICT"),
    required=False,
)

args = parser.parse_args()

if args.dictionary is None:
    logger.error("Missing required parameter --dictionary.")
    sys.exit(1)

main(args)
