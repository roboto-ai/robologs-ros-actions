import argparse
import os
import pathlib
import json
import shutil
import datetime
import cv2
from typing import Optional, List, Tuple, Union

from roboto.domain import actions
from robologs_ros_utils.sources.ros1 import argument_parsers, ros_utils, ros_img_tools
from robologs_ros_utils.utils import file_utils
from ultralytics import YOLO


ALLOWED_MODELS = [
    "yolov8n",
    "yolov8s",
    "yolov8m",
    "yolov8l",
    "yolov8x",
    "yolov8n-seg",
    "yolov8s-seg",
    "yolov8m-seg",
    "yolov8l-seg",
    "yolov8x-seg",
]


def get_images(
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
            process_rosbag(
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
            )

    elif os.path.isfile(input_file_or_folder):
        process_rosbag(
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
        )
    else:
        raise ValueError(
            f"'{input_file_or_folder}' is neither a valid file nor a directory."
        )


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


def run_detector_on_folders(
    root_output_folder: str,
    model_name: str = "yolov8n.pt",
    visualize: bool = False,
    save_video: bool = False,
) -> None:
    """
    Run detector on each image in topic folders that have a img_manifest.json.

    Args:
        root_output_folder (str): Root folder containing the output of the get_images action
        model_name (str): Model name to use for inference: allowed values are yolov8n,
        yolov8s, yolov8m, yolov8l, yolov8x
        visualize (bool): True to draw bounding boxes
        save_video (bool): True to save videos with visualized bounding boxes

    Returns: None

    """
    temp_dir = os.path.join(root_output_folder, "temp_imgs") if save_video else None

    # Iterate over directories
    for bag_dir in os.listdir(root_output_folder):
        bag_path = os.path.join(root_output_folder, bag_dir)

        # Process topic directories inside the bag's output folder
        if os.path.isdir(bag_path):
            for topic_dir in os.listdir(bag_path):
                # Create temporary directory if needed
                if save_video:
                    os.makedirs(temp_dir, exist_ok=True)

                process_topic_directory(
                    topic_dir=topic_dir,
                    bag_path=bag_path,
                    model_name=model_name,
                    visualize=visualize,
                    save_video=save_video,
                    temp_dir=temp_dir,
                )


def process_topic_directory(
    topic_dir: str,
    bag_path: str,
    model_name: str,
    visualize: bool,
    save_video: bool,
    temp_dir: Optional[str],
) -> None:
    """
    Helper function to process a given topic directory.

    Args:
        topic_dir (str): Directory containing the images and manifest file
        bag_path (str): Path to the bag directory
        model_name (str): Model name to use for inference
        visualize (bool): True to draw bounding boxes
        save_video (bool): True to save videos with visualized bounding boxes
        temp_dir (str): Temporary directory to save images to

    Returns: None
    """

    topic_path = os.path.join(bag_path, topic_dir)
    manifest_path = os.path.join(topic_path, "img_manifest.json")

    # Continue only if manifest exists
    if not os.path.isfile(manifest_path):
        return

    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    frame_rate = round(manifest["topic"]["Frequency"], 2)
    detections = {
        "images": {},
        "metadata": {
            "model_name": model_name,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
    }

    for image_data in manifest["images"].values():
        detections["images"][image_data["img_name"]], img = run_detect(
            image_path=image_data["path"],
            model_name=model_name,
            visualize=visualize,
            create_video=save_video,
        )

        # Save processed image if needed
        if save_video:
            cv2.imwrite(os.path.join(temp_dir, image_data["img_name"]), img)

    # Save detections to file
    with open(os.path.join(topic_path, "detections.json"), "w") as f:
        json.dump(detections, f, indent=4)

    # Create video if required
    if save_video:
        print(temp_dir, topic_path, frame_rate)
        ros_img_tools.create_video_from_images(
            input_path=temp_dir, output_path=topic_path, frame_rate=frame_rate
        )
        shutil.rmtree(temp_dir)

    move_images_to_subfolder(topic_path)


def move_images_to_subfolder(topic_path: str) -> None:
    """
    Move all images (.jpg, .jpeg, .png) from the specified directory to a subfolder named "imgs".

    Parameters:
    - topic_path (str): Path to the directory containing the images.
    """
    # Create the 'imgs' subfolder if it doesn't exist
    img_folder = os.path.join(topic_path, "imgs")
    if not os.path.exists(img_folder):
        os.makedirs(img_folder)

    # Walk through the files in the topic_path
    for root, _, files in os.walk(topic_path):
        for file in files:
            # Check if the file has one of the desired extensions
            if file.lower().endswith((".jpg", ".jpeg", ".png", "json")):
                # Create the source path for the file
                src_path = os.path.join(root, file)
                # Create the destination path for the file inside the 'imgs' subfolder
                dest_path = os.path.join(img_folder, file)
                # Move the file to the 'imgs' subfolder
                shutil.move(src_path, dest_path)


def run_detect(
    image_path: str,
    model_name: str,
    visualize: bool = False,
    create_video: bool = False,
) -> Tuple[Union[None, str], Union[None, str]]:
    """
    Runs the YOLO detector on the provided image.

    Parameters:
    - image_path (str): Path to the image file.
    - ... (additional parameters with their descriptions)

    Returns:
    - Tuple of JSON results and optionally the processed image.
    """

    global model  # Ensure model is loaded only once
    if "model" not in globals():
        model = YOLO(f"{model_name}.pt")

    img = cv2.imread(image_path, -1)
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    # Run detection
    start_time = datetime.datetime.now()
    results = model(img)
    end_time = datetime.datetime.now()

    delta = end_time - start_time
    print(
        f"Detection on {os.path.basename(image_path)} took {int(delta.total_seconds() * 1000)} ms"
    )

    if visualize:
        img = results[0].plot()
        cv2.imwrite(image_path, img)

    if create_video:
        img = results[0].plot()
    return json.loads(results[0].tojson(normalize=True)), img if len(
        results
    ) == 1 else (None, None)


parser = argparse.ArgumentParser()
parser.add_argument(
    "-i",
    "--input-dir",
    dest="input_dir",
    type=pathlib.Path,
    required=False,
    help="Directory containing input files to process",
    default=os.environ.get("ROBOTO_INPUT_DIR"),
)
parser.add_argument(
    "-o",
    "--output-dir",
    dest="output_dir",
    type=pathlib.Path,
    required=False,
    help="Directory to which to write any output files to be uploaded",
    default=os.environ.get("ROBOTO_OUTPUT_DIR"),
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
    type=int,
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
    help="Set True to save videos with visualized bounding boxes",
    default=(os.environ.get("ROBOTO_PARAM_SAVE_VIDEO", "True") == "True"),
)

parser.add_argument(
    "--visualize",
    action="store_true",
    required=False,
    help="Draw bounding boxes on images",
    default=(os.environ.get("ROBOTO_PARAM_VISUALIZE") == "True"),
)

parser.add_argument(
    "--model-name",
    type=str,
    required=False,
    help="Model name to use for inference: allowed values are yolov8n, yolov8s, yolov8m, yolov8l, yolov8x",
    default=os.environ.get("ROBOTO_PARAM_MODEL_NAME", "yolov8n"),
)

args = parser.parse_args()

if args.model_name not in ALLOWED_MODELS:
    raise ValueError(
        f"Invalid MODEL_NAME '{args.model_name}'. Allowed values are {', '.join(ALLOWED_MODELS)}"
    )

if args.save_video:
    args.manifest = True

get_images(
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
)


run_detector_on_folders(
    root_output_folder=args.output_dir,
    model_name=args.model_name,
    visualize=args.visualize,
    save_video=args.save_video,
)
