import argparse
import os
from typing import List
import logging
import sys
import pathlib
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

from roboto.association import (
    Association,
    AssociationType,
)
from roboto.domain import actions, datasets, files, topics
from roboto.http import (
    HttpClient,
    SigV4AuthDecorator,
)
from roboto.transactions import TransactionManager

import ros_ingestion.utils as utils

log = logging.getLogger("Ingesting rosbag files to Roboto")


def load_env_var(env_var: actions.InvocationEnvVar) -> str:
    """
    Load an environment variable, and exit if it is not found.

    Args:
    - env_var: The environment variable to load.

    Returns:
    - The value of the environment variable.
    """
    value = os.getenv(env_var.value)
    if not value:
        log.error("Missing required ENV var: '%s'", env_var)
        sys.exit(1)
    return value


def setup_env():
    """
    Set up the environment for the action.

    Returns:
    - A tuple containing the organization ID, input directory, output directory, topic delegate, and dataset.
    """
    roboto_service_url = load_env_var(actions.InvocationEnvVar.RobotoServiceUrl)
    org_id = load_env_var(actions.InvocationEnvVar.OrgId)
    invocation_id = load_env_var(actions.InvocationEnvVar.InvocationId)
    input_dir = load_env_var(actions.InvocationEnvVar.InputDir)
    output_dir = load_env_var(actions.InvocationEnvVar.OutputDir)

    http_client = HttpClient(default_auth=SigV4AuthDecorator("execute-api"))

    topic_delegate = topics.TopicHttpDelegate(
        roboto_service_base_url=roboto_service_url, http_client=http_client
    )

    invocation = actions.Invocation.from_id(
        invocation_id,
        invocation_delegate=actions.InvocationHttpDelegate(
            roboto_service_base_url=roboto_service_url, http_client=http_client
        ),
        org_id=org_id,
    )
    dataset = datasets.Dataset.from_id(
        invocation.data_source.data_source_id,
        datasets.DatasetHttpDelegate(
            roboto_service_base_url=roboto_service_url, http_client=http_client
        ),
        files.FileClientDelegate(
            roboto_service_base_url=roboto_service_url, http_client=http_client
        ),
        transaction_manager=TransactionManager(
            roboto_service_base_url=roboto_service_url, http_client=http_client
        ),
    )

    return org_id, input_dir, output_dir, topic_delegate, dataset


def process_data(
    ros_file_path,
    mcap_file_path,
    topic_object,
    output_dir_path_topics,
    output_dir_temp,
):
    """
    This  function creates per-topic MCAP files and uploads them to Roboto.

    Args:
    - ros_file_path: The path to the ROS bag file.
    - mcap_file_path: The path to the MCAP file.
    - topic_object: The topic object.
    - output_dir_path_topics: The output directory path for the topics.
    - output_dir_temp: The output directory path for temporary files.

    Returns:
    - None
    """
    org_id, input_dir, output_dir, topic_delegate, dataset = setup_env()

    dataset_relative_path = pathlib.Path(ros_file_path).relative_to(input_dir)
    file_record = dataset.get_file_info(dataset_relative_path)

    topic_association = Association(
        association_id=file_record.file_id, association_type=AssociationType.File
    )

    topic_name = topic_object[0]
    schema_name = topic_object[1].name
    schema_checksum = topic_object[2]
    channel_msg_count = topic_object[3]
    start_time_ns = topic_object[4]
    end_time_ns = topic_object[5]

    topic_name_fix = topic_name.replace("/", "_")

    topic = topics.Topic.create(
        request=topics.CreateTopicRequest(
            association=topic_association,
            org_id=org_id,
            schema_name=schema_name,
            schema_checksum=schema_checksum,
            topic_name=topic_name_fix,
            message_count=channel_msg_count,
            start_time=start_time_ns,
            end_time=end_time_ns,
        ),
        topic_delegate=topic_delegate,
    )
    print(f"Topic created: {topic_name_fix}")

    # Create Message Path Records
    relative_file_name = ros_file_path.split(input_dir)[1][1:]
    utils.create_message_path_records(topic, topic_object)
    print(
        f"https://app-beta.roboto.ai/visualize/{utils.generate_config(file_record.file_id, relative_file_name)}"
    )

    # Create MCAP File
    output_path_per_topic_mcap = utils.split_mcap_file_per_topic(
        mcap_file_path, output_dir_path_topics, topic_name
    )
    print(f"MCAP file path: {output_path_per_topic_mcap}")

    relative_file_name = output_path_per_topic_mcap.split(output_dir_temp)[1][1:]

    # Upload MCAP File
    dataset.upload_file(pathlib.Path(output_path_per_topic_mcap), relative_file_name)

    file_id = dataset.get_file_info(relative_file_name).file_id

    print(
        f"Setting default representation for topic: {topic_name_fix}, file_id: {file_id}"
    )

    # Set Default Topic Representation
    topic.set_default_representation(
        request=topics.SetDefaultRepresentationRequest(
            association=Association(
                association_type=AssociationType.File,
                association_id=file_id,
            ),
            org_id=org_id,
            storage_format=topics.RepresentationStorageFormat.MCAP,
            version=1,
        )
    )
    return None


def ingest_ros(ros_file_path: str, topics: List[str] = None):
    """
    This function ingests ROS bag files into Roboto for visualization.

    Args:
    - ros_file_path: The path to the ROS bag file.
    - topics: The list of topics to process.

    Returns:
    - None
    """

    topics = topics.split(",") if topics else None

    # Create MCAP file from ROS bag
    mcap_file_path = ros_file_path.replace(".bag", ".mcap")
    utils.convert_bag_to_mcap(ros_file_path, mcap_file_path)

    _, input_dir, _, _, _ = setup_env()

    output_dir_path_topics, output_dir_temp = utils.setup_output_folder_structure(
        mcap_file_path, input_dir
    )

    start_time = time.time()
    topic_list = utils.get_topics_and_schemas(mcap_path=mcap_file_path)

    topics_to_process = list()
    if topics:
        for topic in topic_list:
            if topic[0] in topics:
                topics_to_process.append(topic)
    else:
        topics_to_process = topic_list

    args_list = [
        (
            ros_file_path,
            mcap_file_path,
            topic_object,
            output_dir_path_topics,
            output_dir_temp,
        )
        for topic_object in topics_to_process
    ]

    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(process_data, *args) for args in args_list]

        for future in as_completed(futures):
            try:
                print("Task completed successfully")
            except Exception as exc:
                print(f"Task generated an exception: {exc}")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"It took {elapsed_time} seconds to process {ros_file_path}.")


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
    "-t",
    "--topic-names",
    dest="topic_names",
    type=str,
    required=False,
    help="List of topic names to process, separated by commas",
    default=os.environ.get("ROBOTO_PARAM_TOPICS", None),
)

args = parser.parse_args()

for root, dirs, f in os.walk(args.input_dir):
    for file in f:
        full_path = os.path.join(root, file)
        if full_path.endswith(".bag"):
            ingest_ros(
                ros_file_path=full_path,
                topics=args.topic_names,
            )
