import os
import sys
import pandas as pd
from bagpy import bagreader
import logging
import argparse
import ast
from robologs_ros_actions.utils import utils

# Setting up the logger
logger = logging.getLogger("test-user-defined-action")
logging.root.handlers = []
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)4s:%(filename)s %(lineno)4s %(asctime)s] %(message)s",
    handlers=[logging.StreamHandler()],  # log to stderr
)


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
        return ast.literal_eval(dict_string)  # Safely parse a string to a Python literal
    except ValueError:
        raise argparse.ArgumentTypeError("Dictionary expected")


def main():
    """
    Main function that sets up command line arguments, checks environment variables,
    and calls the main processing function.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dictionary', type=convert_to_dict, required=True)
    parser.add_argument('-i', '--input_dir', type=str, default=os.getenv('INPUT_DIR'))
    parser.add_argument('-o', '--output_dir', type=str, default=os.getenv('OUTPUT_DIR'))
    args = parser.parse_args()

    if args.input_dir is None:
        logger.error("Missing required input directory.")
        sys.exit(1)

    if args.output_dir is None:
        logger.error("Missing required output directory.")
        sys.exit(1)

    print(f'The dictionary is: {args.dictionary}')

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
    bag_files = utils.get_all_files_of_type_in_directory(
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

                for k in keyword_dict.keys():
                    if df['msg'].str.contains(keyword_dict[k]).any():
                        if k not in tags:
                            tags.append(k)

        except Exception as e:
            # Logging the exception encountered and the file causing it
            logger.error(f"Couldn't read rosbag: {bag_file}. Error: {e}")
            continue

    # Save tags
    utils.save_tags(tag_list=tags)


if __name__ == "__main__":
    main()
