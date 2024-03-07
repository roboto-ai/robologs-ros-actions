import argparse
import os
import pathlib
import json
import shutil
import datetime
import cv2
import glob
from typing import Optional, List, Tuple, Union

from roboto.domain import actions
from roboto.env import RobotoEnvKey
from robologs_ros_utils.sources.ros1 import ros_img_tools
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


def list_all_files(directory):
    """
    List all files in a directory and its subdirectories.

    Parameters:
    - directory (str): The path to the directory to list files from.

    Returns:
    - List[str]: A list of file paths.
    """
    all_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            all_files.append(os.path.join(root, file))
    return all_files


def move_output_files(source_folder: str, destination_folder: str) -> None:
    """
    Moves files with .json and .mp4 extensions from source_folder to destination_folder,
    maintaining the relative folder structure.

    Parameters:
    - source_folder (str): Path to the source folder.
    - destination_folder (str): Path to the destination folder.
    """
    if not os.path.exists(source_folder):
        print(f"Source folder {source_folder} does not exist.")
        return

    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if file.endswith(".json") or file.endswith(".mp4"):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(root, source_folder)
                destination_path = os.path.join(destination_folder, relative_path)

                if not os.path.exists(destination_path):
                    os.makedirs(destination_path)

                shutil.move(file_path, destination_path)
                print(f"Moved {file_path} to {destination_path}")


def process_all_folders(
    input_dir: str,
    model_name: str = "yolov8n.pt",
    save_video: bool = False,
    frame_rate: int = 10,
) -> None:
    """
    Processes all folders in the given input directory using the specified YOLO model.

    Parameters:
    - input_dir (str): Directory containing input files to process.
    - model_name (str): Name of the YOLO model to use for processing.
    - save_video (bool): Flag to indicate if videos should be saved.
    - frame_rate (int): Frame rate for output videos.
    """
    for root, dirs, files in os.walk(input_dir):
        temp_dir = os.path.join(input_dir, "temp_imgs")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        process_image_folder(
            folder_path=root,
            model_name=model_name,
            save_video=save_video,
            frame_rate=frame_rate,
            temp_dir=temp_dir,
        )


def process_image_folder(
    folder_path: str,
    model_name: str,
    save_video: bool,
    frame_rate: int,
    temp_dir: Optional[str],
) -> None:
    """
    Processes images in a given folder using a specified YOLO model.

    Parameters:
    - folder_path (str): Path to the folder containing images.
    - model_name (str): Name of the YOLO model to use for processing.
    - save_video (bool): Flag to indicate if videos should be saved.
    - frame_rate (int): Frame rate for output videos.
    - temp_dir (Optional[str]): Temporary directory for intermediate processing.
    """

    print(f"Processing {folder_path}...")

    file_patterns = ["*.jpg", "*.jpeg", "*.png"]
    image_files = [
        f
        for pattern in file_patterns
        for f in glob.glob(os.path.join(folder_path, pattern))
    ]

    if not image_files:
        print(f"No images found in {folder_path}")

    detections = {
        "images": {},
        "metadata": {
            "model_name": model_name,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
    }

    for image_file in sorted(image_files):
        _, image_name = os.path.split(image_file)
        detections["images"][image_name], img = run_detect(
            image_path=image_file, model_name=model_name, create_video=save_video
        )

        if save_video:
            cv2.imwrite(os.path.join(temp_dir, image_name), img)

    if len(detections["images"]) > 0:
        with open(os.path.join(folder_path, "detections.json"), "w") as f:
            json.dump(detections, f)

    if save_video:
        ros_img_tools.create_video_from_images(
            input_path=temp_dir, output_path=folder_path, frame_rate=frame_rate
        )
        shutil.rmtree(temp_dir)


def run_detect(
    image_path: str,
    model_name: str,
    create_video: bool = False
) -> Tuple[Optional[str], Optional[str]]:
    """
    Runs the YOLO detector on the provided image.

    Parameters:
    - image_path (str): Path to the image file.
    - model_name (str): Name of the YOLO model file (without extension).
    - create_video (bool, optional): Flag to indicate whether to create a video from the detection results.

    Returns:
    Tuple[Optional[str], Optional[str]]: A tuple containing:
        - A JSON string of detection results.
        - The processed image if `create_video` is True; otherwise None.
    """

    global model
    # Load the model only once
    if "model" not in globals():
        model = YOLO(f"{model_name}.pt")

    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"Error reading image {image_path}.")
        return None, None

    if len(img.shape) == 2:  # Convert grayscale to BGR
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    # Run detection and measure time
    start_time = datetime.datetime.now()
    results = model(img)
    end_time = datetime.datetime.now()

    delta = end_time - start_time
    print(f"Detection on {os.path.basename(image_path)} took {delta.total_seconds() * 1000:.0f} ms")

    processed_img = results[0].plot() if create_video else None

    return json.loads(results[0].tojson(normalize=True)), processed_img


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
    "--save_video",
    action="store_true",
    required=False,
    help="Set True to save videos with visualized bounding boxes",
    default=(os.environ.get("ROBOTO_PARAM_SAVE_VIDEO", "True") == "True"),
)

parser.add_argument(
    "--frame_rate",
    type=int,
    required=False,
    help="Desired frame-rate for output video",
    default=os.environ.get("ROBOTO_PARAM_FRAME_RATE", 10),
)

parser.add_argument(
    "--model-name",
    type=str,
    required=False,
    help="Model name for inference: allowed values are yolov8n, yolov8s, yolov8m, yolov8l, yolov8x, \
    yolov8n-seg, yolov8s-seg, yolov8m-seg, yolov8l-seg, yolov8x-seg",
    default=os.environ.get("ROBOTO_PARAM_MODEL_NAME", "yolov8n-seg"),
)

args = parser.parse_args()


files = list_all_files(args.input_dir)
print(f"All files: {files}")
for file in files:
    print(file)

if args.model_name not in ALLOWED_MODELS:
    raise ValueError(
        f"Invalid MODEL_NAME '{args.model_name}'. Allowed values are {', '.join(ALLOWED_MODELS)}"
    )

process_all_folders(
    input_dir=args.input_dir,
    model_name=args.model_name,
    save_video=args.save_video,
    frame_rate=args.frame_rate,
)

move_output_files(args.input_dir, args.output_dir)
