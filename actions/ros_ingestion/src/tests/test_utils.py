import os.path
import shutil
import ros_ingestion.utils as utils
import sys
from mcap_ros1.decoder import DecoderFactory
from mcap.reader import make_reader


def test_mcap(tmp_path):
    with open("./tests/example.mcap", "rb") as f:
        reader = make_reader(f, decoder_factories=[DecoderFactory()])

        # print(dir(reader))
        # print(dir(reader.get_summary()))
        #
        # print(reader.get_summary().channels[8])
        print(reader.get_summary().schemas[1])

        # Assuming the Schema object's data attribute is what you want to format
        data_decoded = reader.get_summary().schemas[1].data.decode('utf-8')  # Decoding using UTF-8, adjust encoding if necessary

        formatted_data = data_decoded.replace('\\n', '\n')  # Ensuring newline characters are interpreted correctly
        print(formatted_data)
        utils.create_message_paths(formatted_data)
        assert True == True
        #
        # input_text = """
        # # This message holds a collection of N-dimensional points, which may
        # # contain additional information such as normals, intensity, etc. The
        # # point data is stored as a binary blob, its layout described by the
        # # contents of the "fields" array.
        #
        # # The point cloud data may be organized 2d (image-like) or 1d
        # # (unordered). Point clouds organized as 2d images may be produced by
        # # camera depth sensors such as stereo or time-of-flight.
        #
        # # Time of sensor data acquisition, and the coordinate frame ID (for 3d
        # # points).
        # Header header
        #
        # # 2D structure of the point cloud. If the cloud is unordered, height is
        # # 1 and width is the length of the point cloud.
        # uint32 height
        # uint32 width
        #
        # # Describes the channels and their layout in the binary data blob.
        # PointField[] fields
        #
        # bool    is_bigendian # Is this data bigendian?
        # uint32  point_step   # Length of a point in bytes
        # uint32  row_step     # Length of a row in bytes
        # uint8[] data         # Actual point data, size is (row_step*height)
        #
        # bool is_dense        # True if there are no invalid points
        #
        # ================================================================================
        # MSG: std_msgs/Header
        # # Standard metadata for higher-level stamped data types.
        # # This is generally used to communicate timestamped data
        # # in a particular coordinate frame.
        # #
        # # sequence ID: consecutively increasing ID
        # uint32 seq
        # #Two-integer timestamp that is expressed as:
        # # * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')
        # # * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')
        # # time-handling sugar is provided by the client library
        # time stamp
        # #Frame this data is associated with
        # string frame_id
        #
        # ================================================================================
        # MSG: sensor_msgs/PointField
        # # This message holds the description of one point entry in the
        # # PointCloud2 message format.
        # uint8 INT8    = 1
        # uint8 UINT8   = 2
        # uint8 INT16   = 3
        # uint8 UINT16  = 4
        # uint8 INT32   = 5
        # uint8 UINT32  = 6
        # uint8 FLOAT32 = 7
        # uint8 FLOAT64 = 8
        #
        # string name      # Name of field
        # uint32 offset    # Offset from start of point struct
        # uint8  datatype  # Datatype enumeration, see above
        # uint32 count     # How many elements in the field
        #
        # other_nested_message_type[] test_nested_message_type
        #
        # ================================================================================
        # MSG: sensor_msgs/other_nested_message_type
        # # This message holds another entry
        # string name
        # """
        #
        # expected_dict_std_msgs_Header = {
        #     "seq": "uint32",
        #     "stamp": "time",
        #     "frame_id": "string"
        # }
        #
        # expected_dict_sensor_msgs_PointField = {
        #     "name": "string",
        #     "offset": "uint32",
        #     "datatype": "uint8",
        #     "count": "uint32",
        #     "INT8": "uint8",
        #     "UINT8": "uint8",
        #     "INT16": "uint8",
        #     "UINT16": "uint8",
        #     "INT32": "uint8",
        #     "UINT32": "uint8",
        #     "FLOAT32": "uint8",
        #     "FLOAT64": "uint8",
        #     "test_nested_message_type": "other_nested_message_type[]"
        # }
        #
        # parsed_schemas = utils.parse_message_schemas(input_text)
        #
        # assert parsed_schemas["Header"] == expected_dict_std_msgs_Header
        #
        # assert parsed_schemas["PointField"] == expected_dict_sensor_msgs_PointField
        #
        # utils.create_message_paths(input_text)
        #
        # for schema_name, fields in parsed_schemas.items():
        #     print(f"{schema_name}: {fields}\n")
        # # for schema, channel, message, ros_msg in reader.iter_decoded_messages():
        # #     print(f"{channel.topic} {schema.name} [{message.log_time}]: {ros_msg}")
        #
        # print(parsed_schemas)
        # utils.create_message_paths(input_text)