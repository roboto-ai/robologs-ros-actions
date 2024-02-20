import os.path
import ros_ingestion.utils as utils


def test_mcap(tmp_path):
    input_text = """
    # This message holds a collection of N-dimensional points, which may
    # contain additional information such as normals, intensity, etc. The
    # point data is stored as a binary blob, its layout described by the
    # contents of the "fields" array.

    # The point cloud data may be organized 2d (image-like) or 1d
    # (unordered). Point clouds organized as 2d images may be produced by
    # camera depth sensors such as stereo or time-of-flight.

    # Time of sensor data acquisition, and the coordinate frame ID (for 3d
    # points).
    Header header

    # 2D structure of the point cloud. If the cloud is unordered, height is
    # 1 and width is the length of the point cloud.
    uint32 height
    uint32 width

    # Describes the channels and their layout in the binary data blob.
    PointField[] fields

    bool    is_bigendian # Is this data bigendian?
    uint32  point_step   # Length of a point in bytes
    uint32  row_step     # Length of a row in bytes
    uint8[] data         # Actual point data, size is (row_step*height)

    bool is_dense        # True if there are no invalid points

    ================================================================================
    MSG: std_msgs/Header
    # Standard metadata for higher-level stamped data types.
    # This is generally used to communicate timestamped data
    # in a particular coordinate frame.
    #
    # sequence ID: consecutively increasing ID
    uint32 seq
    #Two-integer timestamp that is expressed as:
    # * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')
    # * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')
    # time-handling sugar is provided by the client library
    time stamp
    #Frame this data is associated with
    string frame_id

    ================================================================================
    MSG: sensor_msgs/PointField
    # This message holds the description of one point entry in the
    # PointCloud2 message format.
    uint8 INT8    = 1
    uint8 UINT8   = 2
    uint8 INT16   = 3
    uint8 UINT16  = 4
    uint8 INT32   = 5
    uint8 UINT32  = 6
    uint8 FLOAT32 = 7
    uint8 FLOAT64 = 8

    string name      # Name of field
    uint32 offset    # Offset from start of point struct
    uint8  datatype  # Datatype enumeration, see above
    uint32 count     # How many elements in the field

    other_nested_message_type[] test_nested_message_type

    ================================================================================
    MSG: sensor_msgs/other_nested_message_type
    # This message holds another entry
    string name
    """

    expected_dict_std_msgs_Header = {
        "seq": "uint32",
        "stamp": "time",
        "frame_id": "string",
    }

    expected_dict_sensor_msgs_PointField = {
        "name": "string",
        "offset": "uint32",
        "datatype": "uint8",
        "count": "uint32",
        "INT8": "uint8",
        "UINT8": "uint8",
        "INT16": "uint8",
        "UINT16": "uint8",
        "INT32": "uint8",
        "UINT32": "uint8",
        "FLOAT32": "uint8",
        "FLOAT64": "uint8",
        "test_nested_message_type": "other_nested_message_type[]",
    }

    all_schemas, schema_name_lookup = utils.parse_message_schemas(input_text)

    assert all_schemas["Header"] == expected_dict_std_msgs_Header

    assert all_schemas["PointField"] == expected_dict_sensor_msgs_PointField

    message_path_list = utils.create_message_paths(input_text)

    for m in message_path_list:
        if m[0] == "fields.test_nested_message_type":
            assert m[1] == "sensor_msgs/other_nested_message_type[]"


def test_get_channels_mcap(tmp_path):

    mcap_path = "./tests/example.mcap"
    topic_list = utils.get_topics_and_schemas(mcap_path=mcap_path)

    expected_topic = {
        "/rosout": "rosgraph_msgs/Log",
        "/rosout_agg": "rosgraph_msgs/Log",
        "/alphasense/imu": "sensor_msgs/Imu",
        "/alphasense/cam0/image_raw": "sensor_msgs/Image",
        "/alphasense/cam1/image_raw": "sensor_msgs/Image",
        "/alphasense/cam2/image_raw": "sensor_msgs/Image",
        "/alphasense/cam3/image_raw": "sensor_msgs/Image",
        "/alphasense/cam4/image_raw": "sensor_msgs/Image",
        "/hesai/pandar": "sensor_msgs/PointCloud2",
    }

    for entry in topic_list:
        assert entry[0] in expected_topic.keys()
        assert entry[1].name == expected_topic[entry[0]]


def test_convert_bag_to_mcap(tmp_path):
    rosbag_path = "./tests/tiny.bag"
    mcap_path = "./tests/tiny.mcap"

    if os.path.exists(mcap_path):
        os.remove(mcap_path)
    utils.convert_bag_to_mcap(rosbag_path, mcap_path)
    assert os.path.exists(mcap_path)

    if os.path.exists(mcap_path):
        os.remove(mcap_path)


def test_split_mcap_file(tmp_path):

    utils.split_mcap_file("./tests/example.mcap", tmp_path)

    assert os.path.exists(tmp_path / "alphasense_cam0_image_raw.mcap")
    assert os.path.exists(tmp_path / "alphasense_cam1_image_raw.mcap")
    assert os.path.exists(tmp_path / "alphasense_cam2_image_raw.mcap")
    assert os.path.exists(tmp_path / "alphasense_cam3_image_raw.mcap")
    assert os.path.exists(tmp_path / "alphasense_cam4_image_raw.mcap")
    assert os.path.exists(tmp_path / "alphasense_imu.mcap")
    assert os.path.exists(tmp_path / "hesai_pandar.mcap")
    assert os.path.exists(tmp_path / "rosout_agg.mcap")
    assert os.path.exists(tmp_path / "rosout.mcap")


def test_split_mcap_file_per_topic(tmp_path):
    utils.split_mcap_file_per_topic(
        "./tests/example.mcap", tmp_path, "/alphasense/cam0/image_raw"
    )

    assert os.path.exists(tmp_path / "alphasense_cam0_image_raw.mcap")
