import argparse
from glob import glob
import os
import pathlib
import sys
import shutil

import logging

from bagpy.bagreader import rosbag
logger = logging.Logger(name=__name__,level=logging.INFO)

from typing import Optional, List, Tuple, Union
from roboto.env import RobotoEnvKey
from roboto.action_runtime.file_changeset import FilesChangesetFileManager
from roboto.domain import actions, datasets, files, http_delegates
from roboto.http import (
        HttpClient,
        SigV4AuthDecorator
        )
from roboto import updates
from roboto.transactions.transaction_manager import TransactionManager

from robologs_ros_utils.sources.ros1 import argument_parsers, ros_utils
from robologs_ros_utils.utils import file_utils
import numpy as np
import cv2

def load_env_var(env_var: RobotoEnvKey, strict=True) -> Union[str, None]:
    """
    source: https://github.com/roboto-ai/robologs-px4-actions/blob/main/actions/ulog_ingestion/src/ulog_ingestion/__main__.py#L44
    Load an environment variable, and exit if it is not found.

    Args:
    - env_var: The environment variable to load.

    Returns:
    - The value of the environment variable.
    """
    value = os.getenv(env_var.value)
    if not value:
        if strict:
            logger.error("Missing required ENV var: '%s'", env_var)
            sys.exit(1)
        else:
            return None
    return value

def main(
    input_file_or_folder: str,
    output_folder: str,
    manifest: bool = True,
    topics: Optional[str] = None,
    bins: int = 15,
    extract_all_images: Optional[bool] = False,
) -> None:
    """
    Extract images from a Rosbag1 format.

    Args:
        input_file_or_folder (str): Path to the input rosbag or directory of rosbags.
        output_folder (str): Path to the output folder where images will be saved.
        manifest (bool, optional): Whether to create a manifest. Default is True.
        topics (str, optional): Comma-separated list of topics. If None, all image topics are considered.
        bins (int, optional): number of bins for intensity histogram-based exposure analysis. Default 15.
        resize (str, optional): Desired resolution in WIDTHxHEIGHT format or None for no resizing.
        save_video (bool, optional): Set true to save videos.
        extract_all_images (bool, optional): whether to extract and save all image files
    """

    # Roboto dataset setup
    invocation_id = load_env_var(RobotoEnvKey.InvocationId, strict=False)
    service_url = load_env_var(RobotoEnvKey.RobotoServiceUrl, strict=False)

    # If inside an invocation, get info for file-level tagging
    if invocation_id:
        assert service_url is not None, "Error: invocation exists but no service url"
        # Setup and authorize HTTP client
        client = HttpClient(default_auth=SigV4AuthDecorator("execute-api"))
        service_url = load_env_var(RobotoEnvKey.RobotoServiceUrl)

        delegate = http_delegates.HttpDelegates.from_client(http=client, endpoint=service_url)
        invocation = actions.invocation.Invocation.from_id(invocation_id, delegate.invocations)
        dataset_id = invocation.data_source.data_source_id
        transaction_manager = TransactionManager(service_url, client)

        dataset = datasets.dataset.Dataset.from_id(dataset_id, dataset_delegate=delegate.datasets, file_delegate=delegate.files, transaction_manager=transaction_manager)
    else:
        dataset = None
    topics_list = topics.split(",") if topics else None

    if os.path.isdir(input_file_or_folder):
        rosbag_files = file_utils.get_all_files_of_type_in_directory(
            input_folder=input_file_or_folder, file_format="bag"
        )
        # if there are no rosbags and only images/img files, continue
        if not rosbag_files:
            raise FileNotFoundError(
                f"'{input_file_or_folder}' is does not contain any rosbags."
                )

        for rosbag_path in rosbag_files:
            process_rosbag(
                    rosbag_path=rosbag_path,
                    output_folder=output_folder,
                    manifest=manifest,
                    topics=topics_list
                    )

    elif os.path.isfile(input_file_or_folder):
        process_rosbag(
            rosbag_path=input_file_or_folder,
            output_folder=output_folder,
            manifest=manifest,
            topics=topics_list,
        )

    else:
        raise ValueError(
            f"'{input_file_or_folder}' is neither a valid file nor a directory."
        )

    # analyze exposure of images in output directory
    # iterate through each rosbag folder folder first

    output_root = pathlib.Path(output_folder)
    # bag output folers share the name of their input bags
    rosbag_names = [pathlib.Path(p).stem for p in rosbag_files]

    bag_out_folders = [p for p in output_root.iterdir() if p.is_dir() and p.name in rosbag_names]
        
    # setup file changeset manager if in an invocation and extracting all images
    # to enable tagging at the file level
    if dataset and extract_all_images:
        FileManager = FilesChangesetFileManager()

    # enumerate all image paths
    for bag_folder in bag_out_folders:
        bag_put_tags = []
        all_img_paths = []
        for img_ext in ["jpg", "JPG", "JPEG", "png", "PNG"]:
            all_img_paths.extend(glob(f"**/*.{img_ext}", root_dir=str(bag_folder), recursive=True))

        if len(all_img_paths) == 0:
            logger.warning(f"No image files extracted from {bag_folder.name}.bag.")
    
        overexposed_images = []
        underexposed_images = []
        good_images = []
        for img_path in all_img_paths:

            # read in image in grayscale mode
            img = cv2.imread(str(bag_folder / img_path), cv2.IMREAD_GRAYSCALE)
            
            # take a histogram of the image. By default we take 15 bins
            hist = np.histogram(img, bins=bins, range=(0., 255.))[0]
            largest_bin = np.argmax(hist)
            
            # add a file-level tag if image is over or underexposed
            # images with most intensity at the bottom of the histogram are underexposed
            if largest_bin == 0:
                put_tag = "underexposed"
                underexposed_images.append(img_path)
            # images with most intensity at the top of the histogram are overexposed
            elif largest_bin == bins - 1:
                put_tag = "overexposed"
                overexposed_images.append(img_path)
            else:
                put_tag = False
                good_images.append(img_path)
            
            if put_tag:
                bag_put_tags.append(put_tag)
                if dataset and extract_all_images:
                    print(f"putting tag {put_tag} on imag {img_path}")
                    FileManager.put_tags(f"{bag_folder.name}/{img_path}", [put_tag])


        # put tags on rosbag if dataset is not None and put_tags exist
        if dataset: 
            if bag_put_tags:
                #bag_fname = pathlib.Path(input_file_or_folder) / f"{bag_folder.name}.bag"
                bag_fname = f"{bag_folder.name}.bag"
                # build a MetadataChangeset with put_tag direction
                changeset = updates.MetadataChangeset().Builder()
                # put tags on the Changeset builder one at a time
                for tag in set(bag_put_tags): # only tag dataset with each tag value once
                    changeset = changeset.put_tag(tag)
                changeset = changeset.build()
                bag_file = dataset.get_file_info(bag_fname)
                file_update_request = files.file_requests.UpdateFileRecordRequest(metadata_changeset = changeset)
                # pass request to add metadata
                bag_file = bag_file.update(file_update_request)
                logger.info(f"Tagging {bag_fname} with {bag_put_tags}")

        # save some example images, max 5 for each of over and underexposed
        max_overex_examples = min(len(overexposed_images), 5)
        overexposed_examples = overexposed_images[:max_overex_examples]

        if overexposed_examples:
            overexposed_outputs = output_root / f"{bag_folder.name}_overexposed_examples"
            overexposed_outputs.mkdir(parents=True,exist_ok=True)

        # copy overexposed example images to output example dir
            for img_path in overexposed_examples:
                shutil.copy(bag_folder / img_path, overexposed_outputs / pathlib.Path(img_path).name)
        

        max_underex_examples = min(len(underexposed_images), 5)
        underexposed_examples = underexposed_images[:max_underex_examples]
        if underexposed_examples:
            underexposed_outputs = output_root / f"{bag_folder.name}_underexposed_examples"
            underexposed_outputs.mkdir(parents=True, exist_ok=True)

            # copy overexposed example images to output example dir
            for img_path in underexposed_examples:
                shutil.copy(bag_folder / img_path, underexposed_outputs / pathlib.Path(img_path).name)
        
        if not extract_all_images:
            # remove output bag of images that aren't examples
            shutil.rmtree(bag_folder)
        else:
            # apply updates from File Metadata Manager to dataset
            if dataset:
                FileManager.apply_to_dataset(dataset)

def process_rosbag(
    rosbag_path: str,
    output_folder: str,
    manifest: bool,
    topics: Optional[List[str]],
) -> List[str]:
    """
    Process a single rosbag and extract images.

    Args:
        rosbag_path (str): Path to the rosbag.
        output_folder (str): Path to the output folder.
        manifest (bool): Whether to create a manifest file.
        topics (List[str], optional): List of topics to consider.
        resize (Tuple[int, int], optional): Resolution to resize images to.
        sample (int, optional): Sampling rate for images.

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
        file_format="jpg",
        topics=topics,
        create_manifest=manifest,
        naming="sequential",
    )


parser = argparse.ArgumentParser()

parser.add_argument(
    "-i",
    "--input-dir",
    dest="input_dir",
    type=pathlib.Path,
    required=False,
    help="Directory containing input files to process",
    default=load_env_var(RobotoEnvKey.InputDir),
)
parser.add_argument(
    "-o",
    "--output-dir",
    dest="output_dir",
    type=pathlib.Path,
    required=False,
    help="Directory to which to write any output files to be uploaded",
    default=load_env_var(RobotoEnvKey.OutputDir),
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
    "--bins",
    type=str,
    required=False,
    help="Number of bins in image intensity histogram for analyzing exposure",
    default=os.environ.get("ROBOTO_PARAM_BINS"),
)

parser.add_argument(
    "--extract_all_images",
    action="store_true",
    required=False,
    help="Set True to extract all images and tag at the file level",
    default=(os.environ.get("ROBOTO_PARAM_EXTRACT_ALL_IMAGES") == "True"),
)

args = parser.parse_args()


main(
    input_file_or_folder=args.input_dir,
    output_folder=args.output_dir,
    manifest=args.manifest,
    topics=args.topics,
    extract_all_images=args.extract_all_images
)
