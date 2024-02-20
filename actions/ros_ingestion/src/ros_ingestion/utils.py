from roboto.domain import topics
from mcap_ros1.decoder import DecoderFactory
from mcap.reader import make_reader
from mcap.records import Channel, Message, Schema
from mcap.writer import Writer
import subprocess
import os
import tempfile
from typing import Tuple, Any
import base64
import json


TYPE_MAPPING_CANONICAL = {
    "bool": topics.CanonicalDataType.Number,
    "int8": topics.CanonicalDataType.Number,
    "uint8": topics.CanonicalDataType.Number,
    "int16": topics.CanonicalDataType.Number,
    "uint16": topics.CanonicalDataType.Number,
    "int32": topics.CanonicalDataType.Number,
    "uint32": topics.CanonicalDataType.Number,
    "int64": topics.CanonicalDataType.Number,
    "uint64": topics.CanonicalDataType.Number,
    "float32": topics.CanonicalDataType.Number,
    "float64": topics.CanonicalDataType.Number,
    "string": topics.CanonicalDataType.String,
}


def parse_message_definition(definition: str):
    """
    This function parses a ROS message definition and returns a dictionary with the field name as the key and the field
    type as the value.

    Args:
    - definition: The ROS message definition.

    Returns:
    - field_dict: A dictionary with the field name as the key and the field type as the value.
    """
    field_dict = {}
    for line in definition.split("\n"):
        stripped_line = line.strip()

        if stripped_line.startswith("#") or not stripped_line:
            continue

        # TODO: Look into byte fiels which is not a standard field type, but which appears in rosgraph_msgs/Log
        if stripped_line.startswith("byte") or not stripped_line:
            continue
        if (
            "================================================================================"
            in stripped_line
        ):
            break

        parts = stripped_line.split()
        if len(parts) >= 2:
            field_type = parts[0]
            field_name = parts[1]
            field_dict[field_name] = field_type
    return field_dict


def recursive_function(field_name, field_type, parsed_schemas, results):
    """
    This function recursively processes the message definition to extract the message paths.

    Args:
    - field_name: The name of the field.
    - field_type: The type of the field.
    - parsed_schemas: The parsed schemas.
    - results: The list of results.

    Returns:
    - None
    """

    results.append((field_name, field_type))

    field_type_without_array = field_type.split("[")[0]

    if field_type_without_array == "time":
        field_name_n = field_name + ".secs"
        results.append((field_name_n, "uint32"))
        field_name_n = field_name + ".nsecs"
        results.append((field_name_n, "uint32"))
        return

    if field_type_without_array == "duration":
        field_name_n = field_name + ".secs"
        results.append((field_name_n, "int32"))
        field_name_n = field_name + ".nsecs"
        results.append((field_name_n, "int32"))
        return

    if field_type_without_array in TYPE_MAPPING_CANONICAL.keys():

        if "[" in field_type:
            field_name_n = field_name + ".[*]"
            results.append((field_name_n, field_type_without_array))

        return

    if field_type_without_array in parsed_schemas.keys():
        for key in parsed_schemas[field_type_without_array].keys():
            field_name_n = field_name + "." + key
            recursive_function(
                field_name_n,
                parsed_schemas[field_type_without_array][key],
                parsed_schemas,
                results,
            )


def create_message_paths(input_text):
    """
    This function creates message paths from a ROS message definition.

    Args:
    - input_text: The ROS message definition.

    Returns:
    - message_path_list: The list of message paths.
    """

    message_path_list = list()

    field_dict = parse_message_definition(input_text)

    parsed_schemas, schema_name_lookup = parse_message_schemas(input_text)

    results = []
    for field_name, field_type in field_dict.items():
        recursive_function(field_name, field_type, parsed_schemas, results)

    for it, item in enumerate(results):
        field_type_without_array = item[1].split("[")[0]

        if field_type_without_array in schema_name_lookup.keys():
            if "[" in item[1]:
                schema_name = schema_name_lookup[field_type_without_array] + "[]"
                results[it] = (item[0], schema_name)
            else:
                results[it] = (item[0], schema_name_lookup[field_type_without_array])

        message_path_list.append(results[it])
    return message_path_list


def parse_message_schemas(input_text):
    """
    This function parses the schemas from a ROS message definition.

    Args:
    - input_text: The ROS message definition.

    Returns:
    - all_schemas: A dictionary with the schema name as the key and the schema fields as the value.
    - schema_name_lookup: A dictionary with the original schema name as the key and the schema name as the value.
    """
    all_schemas = {}
    schema_name_lookup = {}
    sections = input_text.split(
        "================================================================================"
    )

    # Process each section to extract schema information
    for section in sections:
        # Split the section into lines for processing
        lines = section.strip().split("\n")
        if not lines:
            continue

        if lines[0].startswith("MSG:"):
            schema_name = lines[0].split("MSG:")[1].strip().split("/")[1]
            schema_name_lookup[schema_name] = lines[0].split("MSG:")[1].strip()

            fields = {}

            for line in lines[1:]:
                line = line.strip()
                if line.startswith("#") or not line:
                    continue

                if "=" in line:
                    continue

                parts = line.split()
                if len(parts) < 2:
                    continue

                field_type = parts[0]
                field_name = parts[1]

                fields[field_name] = field_type

            all_schemas[schema_name] = fields

    return all_schemas, schema_name_lookup


def get_topics_and_schemas(mcap_path: str):
    """
    This function gets the topics and schemas from an MCAP file.

    Args:
    - mcap_path: The path to the MCAP file.

    Returns:
    - topic_list: The list of (topic name, schema, checksum, msg_count, start_time, end_time).
    """
    topic_list = list()

    with open(mcap_path, "rb") as f:
        reader = make_reader(f, decoder_factories=[DecoderFactory()])

        channels = reader.get_summary().channels
        schemas = reader.get_summary().schemas
        statistics = reader.get_summary().statistics

        for key in channels:
            schema_id = channels[key].schema_id
            channel_msg_count = statistics.channel_message_counts[key]
            message_start_time = statistics.message_start_time
            message_end_time = statistics.message_end_time
            topic_tuple = (
                channels[key].topic,
                schemas[schema_id],
                channels[key].metadata["md5sum"],
                channel_msg_count,
                message_start_time,
                message_end_time,
            )

            topic_list.append(topic_tuple)

    return topic_list


def convert_bag_to_mcap(input_bag_file: str, output_mcap_file: str):
    """
    This function converts a ROS bag file to an MCAP file.

    Args:
    - input_bag_file: The path to the ROS bag file.
    - output_mcap_file: The path to the MCAP file.

    Returns:
    - None
    """
    try:
        command = f"mcap convert '{input_bag_file}' '{output_mcap_file}'"
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode == 0:
            print("Conversion successful.")
        else:
            print(f"Conversion failed with error: {result.stderr.decode('utf-8')}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during conversion: {e.stderr.decode('utf-8')}")


def setup_output_folder_structure(
    mcap_file_path: str, input_dir: str
) -> Tuple[str, str]:
    """
    This function sets up the output folder structure for the visualization assets.

    Args:
    - mcap_file_path: The path to the MCAP file.
    - input_dir: The input directory.

    Returns:
    - output_folder_path: The path to the output folder.
    - temp_dir: The path to the temporary directory.
    """
    relative_folder_path_of_file = os.path.split(mcap_file_path.split(input_dir)[1])[0]

    mcap_file_name = os.path.split(mcap_file_path)[1]

    output_folder_name_mcap = mcap_file_name.replace(".mcap", "")
    relative_folder_path_of_file = relative_folder_path_of_file.lstrip("/")
    temp_dir = str(tempfile.TemporaryDirectory().name)

    output_folder_path = os.path.join(
        temp_dir,
        ".VISUALIZATION_ASSETS",
        relative_folder_path_of_file,
        output_folder_name_mcap,
    )

    print(f"Output folder path: {output_folder_path}")
    os.makedirs(output_folder_path, exist_ok=True)

    return output_folder_path, temp_dir


def create_message_path_records(topic: Any, topic_object: Any) -> None:
    """
    This function creates message path records for a topic.

    Args:
    - topic: The topic.
    - topic_object: The topic object.

    Returns:
    - None
    """

    message_path_list = create_message_paths(topic_object[1].data.decode("utf-8"))

    print(f"Message path list: {message_path_list}")

    for entry in message_path_list:
        message_path_name = entry[0]
        message_path_type = entry[1]

        if "[" in message_path_type:
            topic.add_message_path(
                request=topics.AddMessagePathRequest(
                    message_path=message_path_name,
                    data_type=message_path_type,
                    canonical_data_type=topics.CanonicalDataType.Array,
                )
            )

            print(
                f"Adding array: {message_path_name}, type: {message_path_type}, canonical: {topics.CanonicalDataType.Array}"
            )

        else:

            if message_path_type not in TYPE_MAPPING_CANONICAL.keys():
                canonical_data_type = topics.CanonicalDataType.Object
            else:
                canonical_data_type = TYPE_MAPPING_CANONICAL[message_path_type]

            # Add another message path for the array elements
            topic.add_message_path(
                request=topics.AddMessagePathRequest(
                    message_path=message_path_name,
                    data_type=message_path_type,
                    canonical_data_type=canonical_data_type,
                )
            )

            print(
                f"Adding sub-field for array: {message_path_name}, type: {message_path_type}, canonical: {canonical_data_type}"
            )

    return


# Helper function. Will be deleted.
def generate_config(file_id, relative_path):
    viz_config = {
        "version": "v1",
        "files": [{"fileId": file_id, "relativePath": relative_path}],
    }
    return base64.urlsafe_b64encode(json.dumps(viz_config).encode("utf-8")).decode(
        "utf-8"
    )


# Copied from: https://github.com/sensmore/kappe/blob/master/src/kappe/cut.py#L40
class SplitWriter:
    def __init__(self, path: str, profile: str) -> None:
        self._schema_lookup: dict[int, int] = {}
        self._channel_lookup: dict[int, int] = {}

        self.static_tf_set = False
        self.static_tf_channel_id = None
        self.static_tf: list[bytes] | None = None

        self._writer = Writer(path)
        self._writer.start(profile=profile)

    def set_static_tf(
        self, schema: Schema, channel: Channel, data: list[bytes]
    ) -> None:
        self.static_tf_set = True
        self.static_tf_channel_id = self.register_channel(schema, channel)
        self.static_tf = data

    def register_schema(self, schema: Schema) -> int:
        schema_id = self._schema_lookup.get(schema.id, None)
        if schema_id is None:
            schema_id = self._writer.register_schema(
                schema.name,
                schema.encoding,
                schema.data,
            )
            self._schema_lookup[schema.id] = schema_id

        return schema_id

    def register_channel(self, schema: Schema, channel: Channel) -> int:
        channel_id = self._channel_lookup.get(channel.id, None)
        if channel_id is None:
            schema_id = self.register_schema(schema)
            channel_id = self._writer.register_channel(
                channel.topic,
                channel.message_encoding,
                schema_id,
                channel.metadata,
            )
            self._channel_lookup[channel.id] = channel_id

        return channel_id

    def write_message(self, schema: Schema, channel: Channel, message: Message) -> None:
        if self.static_tf is not None and self.static_tf_channel_id is not None:
            for data in self.static_tf:
                self._writer.add_message(
                    self.static_tf_channel_id,
                    message.log_time,
                    data,
                    message.publish_time,
                    message.sequence,
                )
            self.static_tf = None
            self.static_tf_channel_id = None

        if self.static_tf_set and channel.topic == "/tf_static":
            return

        channel_id = self.register_channel(schema, channel)

        self._writer.add_message(
            channel_id,
            message.log_time,
            message.data,
            message.publish_time,
            message.sequence,
        )

    def finish(self) -> None:
        self._writer.finish()


def split_mcap_file(mcap_file_path: str, output_folder: str):
    """
    This function splits an MCAP file into per-topic MCAP files.

    Args:
    - mcap_file_path: The path to the MCAP file.
    - output_folder: The output folder.

    Returns:
    - None
    """
    output_dict = dict()

    topic_list = get_topics_and_schemas(mcap_path=mcap_file_path)

    # TODO: look into parallelization
    with open(mcap_file_path, "rb") as f:
        reader = make_reader(f)
        profile = reader.get_header().profile

        for entry in topic_list:
            mcap_name = entry[0].replace("/", "_")[1:] + ".mcap"
            output_path = os.path.join(output_folder, mcap_name)
            output_dict[entry[0]] = SplitWriter(output_path, profile)

        for schema, channel, message in reader.iter_messages():
            if channel.topic in output_dict.keys():
                output_dict[channel.topic].write_message(schema, channel, message)
            else:
                raise ValueError(f"Channel not found: {channel.topic}")

        for key in output_dict.keys():
            output_dict[key].finish()


def split_mcap_file_per_topic(mcap_file_path: str, output_folder: str, topic_name: str):
    """
    This function splits an MCAP file into per-topic MCAP files for a given topic.

    Args:
    - mcap_file_path: The path to the MCAP file.
    - output_folder: The output folder.
    - topic_name: The topic name to extract.

    Returns:
    - output_path: The path to the output MCAP file.

    """

    with open(mcap_file_path, "rb") as f:
        reader = make_reader(f)
        profile = reader.get_header().profile

        mcap_name = topic_name.replace("/", "_")[1:] + ".mcap"
        output_path = os.path.join(output_folder, mcap_name)

        output = SplitWriter(output_path, profile)

        for schema, channel, message in reader.iter_messages():
            if channel.topic == topic_name:
                output.write_message(schema, channel, message)

        output.finish()

    return output_path
