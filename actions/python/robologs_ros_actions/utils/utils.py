import os
import glob
import json
from typing import List


def get_all_files_of_type_in_directory(input_folder: str, file_format: str) -> list:
    """
    This function gets a list of all files of type "file_format" in a directory
    Args:
        input_folder (str): input folder path

    Returns: list with .pdf files

    """

    subfolder_list = list_all_subfolders(input_folder)

    file_string = f"./*.{file_format}"
    ll = list()
    # look for files in subfolders
    print(subfolder_list)
    for entry in subfolder_list:
        ll = ll + sorted(glob.glob(os.path.abspath(os.path.join(entry, file_string))))

    # look for files in folder
    ll = ll + sorted(glob.glob(os.path.abspath(os.path.join(input_folder, file_string))))
    return ll


def list_all_subfolders(folder_path):
    subfolders = []

    for root, dirs, files in os.walk(folder_path):
        for directory in dirs:
            subfolder_path = os.path.join(root, directory)
            subfolders.append(subfolder_path)

    return subfolders


def save_dataset_md_changeset_json(add_tag_list: List[str],
                                   remove_tag_list: List[str],
                                   metadata_dict: dict,
                                   output_path: str) -> None:
    """
    This function creates a changeset JSON for the dataset and save it to the output path.

    Args:
        add_tag_list (List[str]): A list of tags to add to the robot run.
        remove_tag_list (List[str]): A list of tags to remove from the robot run.
        metadata_dict (dict): A dictionary of metadata to add to the robot run.
        output_path (str): The path to save the changeset JSON.

    Returns:
        None
    """
    changeset_json = dict()
    changeset_json["addTags"] = add_tag_list
    changeset_json["removeTags"] = remove_tag_list
    changeset_json["metadata"] = metadata_dict

    with open(output_path, "w") as output_path:
        json.dump(changeset_json, output_path)

    return


def save_tags(tag_list: List[str]) -> None:
    output_dir = os.getenv("OUTPUT_DIR")

    # Save changeset JSON
    output_path_changeset = os.path.join(output_dir, "dataset_md_changeset.json")
    save_dataset_md_changeset_json(add_tag_list=tag_list,
                                   output_path=output_path_changeset,
                                   remove_tag_list=[],
                                   metadata_dict=dict())

    return



