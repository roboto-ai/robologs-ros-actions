import argparse
import os
import pathlib

from roboto.domain import actions
from robologs_ros_utils.sources.ros1 import ros_utils


def process_topics(value):
    """Function to process topics input."""
    if value:
        return [topic.strip() for topic in value.split(",")]
    else:
        return None


def main(args):
    """
    Extract CSV data from rosbag files and move the CSV files to the specified output directory.
    """

    # Convert topics to list if it's not None
    topic_list = list(args.topics) if args.topics else None

    ros_utils.get_csv_data_from_bag(
        input_dir_or_file=args.input_dir,
        output_dir=args.output_dir,
        topic_list=topic_list,
    )

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
    "--topics",
    "-t",
    type=process_topics,
    help="Comma-separated list of topics to extract",
    default=os.getenv("ROBOTO_PARAM_TOPICS"),
)

args = parser.parse_args()

# Ensure topics are provided
if args.topics is None:
    parser.error("--topics are required if ROBOTO_PARAM_TOPICS is not set")

main(args)
