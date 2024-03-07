import subprocess
import json
import argparse
import pathlib
import os
import re

from typing import List, Dict
from roboto.domain import actions
from roboto.env import RobotoEnvKey


def parse_topics(lines: List[str]) -> List[Dict]:
    """
    Parse topic information from lines.

    :param lines: List of strings containing topic data.
    :return: List of dictionaries with parsed topic information.
    """
    topics = []
    for line in lines:
        if "Topic:" in line:
            parts = line.strip().split("|")

            # Handle the case where 'Topic:' appears twice in the line.
            topic_string = parts[0].split(":")
            if len(topic_string) > 2:
                topic = ":".join(topic_string[2:]).strip()
            else:
                topic = topic_string[1].strip()

            topic_info = {
                "Topic": topic,
                "Type": parts[1].split(":")[1].strip(),
                "Count": int(parts[2].split(":")[1].strip()),
                "SerializationFormat": parts[3].split(":")[1].strip(),
            }
            topics.append(topic_info)
    return topics


def parse_bag_info(db3_path: str) -> Dict:
    """
    Parse information from a .db3 file.

    :param db3_path: File path to the .db3 file.
    :return: Dictionary with parsed .db3 file information.
    """

    cmd = ["ros2", "bag", "info", db3_path]
    output = subprocess.run(cmd, capture_output=True, text=True).stdout
    print(output)
    lines = output.split("\n")
    parsed_info = {}
    for line in lines:
        if "Files:" in line:
            parsed_info["Files"] = line.split(":")[1].strip()
        elif "Bag size:" in line:
            parsed_info["BagSize"] = line.split(":")[1].strip()
        elif "Storage id:" in line:
            parsed_info["StorageId"] = line.split(":")[1].strip()
        elif "Duration:" in line:
            parsed_info["Duration"] = line.split(":")[1].strip()
        elif "Start:" in line:
            # Get only the date portion
            parsed_info["Start_date"] = line.split(":")[1].strip().split("(")[0].strip()
            # Get time portion, if exists
            match_time = re.search(r"\d{2}:\d{2}:\d{2}.\d{3}", line)
            if match_time:
                parsed_info["Start_time"] = match_time.group(0)
            # Get epoch timestamp
            match_epoch = re.search(r"\((.*?)\)", line)
            if match_epoch:
                parsed_info["Start_s"] = str(float(match_epoch.group(1)))
        elif "End:" in line:
            # Get only the date portion
            parsed_info["End"] = line.split(":")[1].strip().split("(")[0].strip()
            # Get time portion, if exists
            match_time = re.search(r"\d{2}:\d{2}:\d{2}.\d{3}", line)
            if match_time:
                parsed_info["End_time"] = match_time.group(0)
            # Get epoch timestamp
            match_epoch = re.search(r"\((.*?)\)", line)
            if match_epoch:
                parsed_info["End_s"] = str(float(match_epoch.group(1)))
        elif "Messages:" in line:
            parsed_info["Messages"] = str(int(line.split(":")[1].strip()))

    # Parsing topics
    topic_lines = [line for line in lines if "Topic:" in line]
    parsed_info["Topics"] = parse_topics(topic_lines)
    return parsed_info


def process_file(input_path: str, output_path: str, hidden: bool = False) -> None:
    """
    Process a single .db3 file and save the parsed info to a .json file.

    :param input_path: File path to the .db3 file.
    :param output_path: Directory path to save the output .json file.
    :param hidden: Boolean indicating if the output .json file should be hidden. Defaults to False.
    """
    parsed_info = parse_bag_info(input_path)

    # Determine the output file name based on the hidden flag
    basename = os.path.basename(input_path) + ".json"
    if hidden:
        basename = "." + basename

    output_file = os.path.join(output_path, basename)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    print(output_file)
    with open(output_file, "w") as f:
        json.dump(parsed_info, f, indent=4)


def process_directory(input_path: str, output_path: str, hidden: bool = False) -> None:
    """
    Process a directory containing .db3 files and save the parsed info to .json files.

    :param input_path: Directory path containing .db3 files.
    :param output_path: Directory path to save the output .json files.
    :param hidden: Boolean indicating if the output .json files should be hidden. Defaults to False.
    """
    for dirpath, _, filenames in os.walk(input_path):
        for filename in filenames:
            if filename.endswith(".db3"):
                rel_dir = os.path.relpath(dirpath, input_path)
                abs_input_file = os.path.join(dirpath, filename)
                abs_output_dir = os.path.join(output_path, rel_dir)
                process_file(abs_input_file, abs_output_dir, hidden)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse db3 file information.")
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i",
        "--input-dir",
        dest="input_dir",
        type=pathlib.Path,
        required=False,
        help="Directory containing input files to process",
        default=os.environ.get(RobotoEnvKey.InputDir.value),
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        dest="output_dir",
        type=pathlib.Path,
        required=False,
        help="Directory to which to write any output files to be uploaded",
        default=os.environ.get(RobotoEnvKey.OutputDir.value),
    )

    parser.add_argument(
        "--hidden",
        action="store_true",
        help="Save the .json files as hidden files",
        default=(os.environ.get("ROBOTO_PARAM_HIDDEN") == "True"),
    )

    args = parser.parse_args()

    if os.path.isfile(args.input_dir):
        if args.input_dir.endswith(".db3"):
            process_file(args.input_dir, args.output_dir, args.hidden)
    elif os.path.isdir(args.input_dir):
        process_directory(args.input_dir, args.output_dir, args.hidden)
    else:
        print(f"Error: {args.input_dir} is neither a file nor a directory.")
