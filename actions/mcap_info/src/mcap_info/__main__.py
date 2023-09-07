import re
import subprocess
import json
import argparse
import os
import pathlib
from typing import List, Dict, Union
from roboto.domain import actions


def parse_channels(lines: List[str]) -> List[Dict]:
    """
    Parse channel information from lines.

    :param lines: List of strings containing channel data.
    :return: List of dictionaries with parsed channel information.
    """
    channels = []
    channel_pattern = re.compile(
        r"\(\d+\) [^ ]+ +\d+ msgs \([\d.]+ Hz\) +: [^ ]+ \[[^\]]+\]"
    )

    for line in lines:
        match = channel_pattern.search(line)
        if match:
            channel_info = {
                "ID": int(re.search(r"\((\d+)\)", line).group(1)),
                "Topic": re.search(r" ([^ ]+) +\d+ msgs", line).group(1),
                "MessageCount": int(re.search(r"(\d+) msgs", line).group(1)),
                "Frequency": float(re.search(r"([\d.]+) Hz", line).group(1)),
                "SchemaName": re.search(r" : ([^ ]+) \[", line).group(1),
                "Encoding": re.search(r"\[([^\]]+)\]", line).group(1),
            }
            channels.append(channel_info)
    return channels


def parse_mcap_info(
    mcap_path: str,
) -> Dict[str, Union[str, int, List[Dict[str, Union[str, int, float]]]]]:
    """
    Parse information from a .mcap file.

    :param mcap_path: File path to the .mcap file.
    :return: Dictionary with parsed .mcap file information.
    """
    cmd = ["mcap", "info", mcap_path]
    output = subprocess.run(cmd, capture_output=True, text=True).stdout
    lines = output.split("\n")
    parsed_info = {}

    # Parsing metadata
    for line in lines:
        if line.startswith("library:"):
            parsed_info["library"] = line.split(":")[1].strip()
        elif line.startswith("profile:"):
            parsed_info["profile"] = line.split(":")[1].strip()
        elif line.startswith("messages:"):
            parsed_info["messages"] = int(line.split(":")[1].strip())
        elif line.startswith("duration:"):
            parsed_info["duration"] = line.split(":")[1].strip()
        elif line.startswith("start:"):
            parsed_info["start"] = line.split(":")[1].split("(")[0].strip()
        elif line.startswith("end:"):
            parsed_info["end"] = line.split(":")[1].split("(")[0].strip()
        elif line.startswith("attachments:"):
            parsed_info["attachments"] = int(line.split(":")[1].strip())
        elif line.startswith("compression:"):
            parsed_info["compression"] = line.split(":")[1].strip()
        elif line.startswith("metadata:"):
            parsed_info["metadata"] = line.split(":")[1].strip()

    # Parsing channels
    start_index = None
    for i, line in enumerate(lines):
        if line.startswith("channels:"):
            start_index = i + 1
            break

    if start_index is not None:
        channels_lines = lines[start_index:]
        parsed_info["channels"] = parse_channels(channels_lines)

    return parsed_info


def process_file(input_path: str, output_path: str, hidden: bool = False) -> None:
    """
    Process a single .mcap file and save the parsed info to a .json file.

    :param input_path: File path to the .mcap file.
    :param output_path: Directory path to save the output .json file.
    :param hidden: Boolean indicating if the output .json file should be hidden. Defaults to False.
    """
    parsed_info = parse_mcap_info(input_path)

    # Determine the output file name based on the hidden flag
    basename = os.path.basename(input_path) + ".json"
    if hidden:
        basename = "." + basename

    output_file = os.path.join(output_path, basename)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(parsed_info, f, indent=4)


def process_directory(input_path: str, output_path: str, hidden: bool = False) -> None:
    """
    Process a directory containing .mcap files and save the parsed info to .json files.

    :param input_path: Directory path containing .mcap files.
    :param output_path: Directory path to save the output .json files.
    :param hidden: Boolean indicating if the output .json files should be hidden. Defaults to False.
    """
    for dirpath, _, filenames in os.walk(input_path):
        for filename in filenames:
            if filename.endswith(".mcap"):
                rel_dir = os.path.relpath(dirpath, input_path)
                abs_input_file = os.path.join(dirpath, filename)
                abs_output_dir = os.path.join(output_path, rel_dir)

                process_file(abs_input_file, abs_output_dir, hidden)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Parse MCAP file information.")
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
        "--hidden",
        action="store_true",
        help="Save the .json files as hidden files",
        default=(os.environ.get("ROBOTO_PARAM_HIDDEN", "False") == "True"),
    )

    args = parser.parse_args()

    if os.path.isfile(args.input_dir):
        process_file(args.input_dir, args.output_dir, args.hidden)
    elif os.path.isdir(args.input_dir):
        process_directory(args.input_dir, args.output_dir, args.hidden)
    else:
        print(f"Error: {args.input_dir} is neither a file nor a directory.")
