import argparse
import os
import pathlib

from typing import Optional, List, Tuple
from roboto.domain import actions
from roboto.env import RobotoEnvKey
from robologs_ros_utils.sources.ros1 import argument_parsers, ros_utils
from robologs_ros_utils.utils import file_utils


def main(
    input_file_or_folder: str,
    output_folder: str,
    file_format: str = "jpg",
    manifest: bool = True,
    topics: Optional[str] = None,
    naming: str = "sequential",
    resize: Optional[str] = None,
    sample: Optional[str] = None,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
    save_video: Optional[bool] = False,
    keep_images: Optional[bool] = False,
) -> None:
    """
    Extract images from a Rosbag1 format.

    Args:
        input_file_or_folder (str): Path to the input rosbag or directory of rosbags.
        output_folder (str): Path to the output folder where images will be saved.
        file_format (str, optional): Desired image format. Default is 'jpg'.
        manifest (bool, optional): Whether to create a manifest. Default is True.
        topics (str, optional): Comma-separated list of topics. If None, all image topics are considered.
        naming (str, optional): Naming schema for output images. Default is 'sequential'.
        resize (str, optional): Desired resolution in WIDTHxHEIGHT format or None for no resizing.
        sample (str, optional): Sampling rate or None for no sampling.
        start_time (float, optional): Start time for extraction or None for the beginning.
        end_time (float, optional): End time for extraction or None for the end.
        save_video (bool, optional): Set true to save videos.
        keep_images (bool, optional): Set true to keep images when using --save_video.
    """

    topics_list = topics.split(",") if topics else None
    resize_dims = (
        argument_parsers.get_width_height_from_args(resize) if resize else None
    )
    sample_rate = int(sample) if sample else None

    if os.path.isdir(input_file_or_folder):
        rosbag_files = file_utils.get_all_files_of_type_in_directory(
            input_folder=input_file_or_folder, file_format="bag"
        )
        for rosbag_path in rosbag_files:
            process_and_maybe_save_video(
                rosbag_path,
                output_folder,
                file_format,
                manifest,
                topics_list,
                naming,
                resize_dims,
                sample_rate,
                start_time,
                end_time,
                save_video,
                keep_images,
            )

    elif os.path.isfile(input_file_or_folder):
        process_and_maybe_save_video(
            input_file_or_folder,
            output_folder,
            file_format,
            manifest,
            topics_list,
            naming,
            resize_dims,
            sample_rate,
            start_time,
            end_time,
            save_video,
            keep_images,
        )

    else:
        raise ValueError(
            f"'{input_file_or_folder}' is neither a valid file nor a directory."
        )


def process_and_maybe_save_video(
    rosbag_path: str,
    output_folder: str,
    file_format: str,
    manifest: bool,
    topics: Optional[List[str]],
    naming: str,
    resize: Optional[Tuple[int, int]],
    sample: Optional[int],
    start_time: Optional[float],
    end_time: Optional[float],
    save_video: Optional[bool],
    keep_images: Optional[bool],
) -> None:
    folder_list = process_rosbag(
        rosbag_path,
        output_folder,
        file_format,
        manifest,
        topics,
        naming,
        resize,
        sample,
        start_time,
        end_time,
    )

    if save_video and folder_list:
        for folder in folder_list:
            ros_utils.get_video_from_image_folder(folder, keep_images)


def process_rosbag(
    rosbag_path: str,
    output_folder: str,
    file_format: str,
    manifest: bool,
    topics: Optional[List[str]],
    naming: str,
    resize: Optional[Tuple[int, int]],
    sample: Optional[int],
    start_time: Optional[float],
    end_time: Optional[float],
) -> List[str]:
    """
    Process a single rosbag and extract images.

    Args:
        rosbag_path (str): Path to the rosbag.
        output_folder (str): Path to the output folder.
        file_format (str): Image format to save as.
        manifest (bool): Whether to create a manifest file.
        topics (List[str], optional): List of topics to consider.
        naming (str): Naming scheme for saved files.
        resize (Tuple[int, int], optional): Resolution to resize images to.
        sample (int, optional): Sampling rate for images.
        start_time (float, optional): Start time for extraction.
        end_time (float, optional): End time for extraction.

    Returns:
        List[str]: List of folders with extracted images.
    """
    bag_name = os.path.splitext(os.path.basename(rosbag_path))[0]
    bag_output_folder = os.path.join(output_folder, bag_name)
    os.makedirs(bag_output_folder, exist_ok=True)
    os.chmod(bag_output_folder, 0o777)

    return ros_utils.get_images_from_bag(
        rosbag_path=rosbag_path,
        output_folder=bag_output_folder,
        file_format=file_format,
        topics=topics,
        create_manifest=manifest,
        naming=naming,
        resize=resize,
        sample=sample,
        start_time=start_time,
        end_time=end_time,
    )


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
    "--format",
    type=str,
    required=False,
    help="Desired image format",
    choices=["jpg", "png"],
    default=os.environ.get("ROBOTO_PARAM_FORMAT", "jpg"),
)

parser.add_argument(
    "--manifest",
    action="store_true",
    required=False,
    help="Whether to save a manifest file",
    default=(os.environ.get("ROBOTO_PARAM_MANIFEST", "True") == "True"),
)

parser.add_argument(
    "--topics",
    type=str,
    required=False,
    help="Comma-separated list of topics",
    default=os.environ.get("ROBOTO_PARAM_TOPICS"),
)

parser.add_argument(
    "--naming",
    type=str,
    required=False,
    help="Naming schema for the output images. Valid values are \
    'sequential', 'rosbag_timestamp', 'msg_timestamp'",
    default=os.environ.get("ROBOTO_PARAM_NAMING", "sequential"),
)

parser.add_argument(
    "--resize",
    type=str,
    required=False,
    help="Desired resolution in WIDTH,HEIGHT format or None for no resizing",
    default=os.environ.get("ROBOTO_PARAM_RESIZE"),
)

parser.add_argument(
    "--sample",
    type=str,
    required=False,
    help="Sampling rate or None for no sampling",
    default=os.environ.get("ROBOTO_PARAM_SAMPLE"),
)

parser.add_argument(
    "--start_time",
    type=float,
    required=False,
    help="Start time for extraction or None for the beginning",
    default=os.environ.get("ROBOTO_PARAM_START_TIME"),
)

parser.add_argument(
    "--end_time",
    type=float,
    required=False,
    help="End time for extraction or None for the end",
    default=os.environ.get("ROBOTO_PARAM_END_TIME"),
)

parser.add_argument(
    "--save_video",
    action="store_true",
    required=False,
    help="Set True to save videos",
    default=(os.environ.get("ROBOTO_PARAM_SAVE_VIDEO") == "True"),
)

parser.add_argument(
    "--keep_images",
    action="store_true",
    required=False,
    help="Set True to keep images when using --save_video",
    default=(os.environ.get("ROBOTO_PARAM_KEEP_IMAGES") == "True"),
)

args = parser.parse_args()

if args.save_video:
    args.manifest = True

main(
    input_file_or_folder=args.input_dir,
    output_folder=args.output_dir,
    file_format=args.format,
    manifest=args.manifest,
    topics=args.topics,
    naming=args.naming,
    resize=args.resize,
    sample=args.sample,
    start_time=args.start_time,
    end_time=args.end_time,
    save_video=args.save_video,
    keep_images=args.keep_images,
)
