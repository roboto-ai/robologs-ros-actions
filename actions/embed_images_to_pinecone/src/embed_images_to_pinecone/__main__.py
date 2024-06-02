import argparse
from glob import glob
import logging
import os
import sys
import pathlib
import json
from typing import Union
import time
from PIL import Image

import torch

from pinecone import Pinecone, ServerlessSpec

from roboto.domain import actions, datasets, files, http_delegates
from roboto.env import RobotoEnvKey
from roboto.http import (
    HttpClient,
    SigV4AuthDecorator,
)
from roboto import updates

from roboto.transactions.transaction_manager import TransactionManager

from transformers import CLIPImageProcessor, CLIPVisionModelWithProjection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# params for timeout
wait_time = 3
timeout = 100

# load cuda if available
# for now this is dead code, because i build pytorch+cpu

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

def main(args):
    
    input_dir = args.input_dir
    output_dir = args.output_dir
    dataset_metadata_path = args.dataset_metadata_path
    files_metadata_path = args.files_metadata_path

    # load pinecone api key from local if not provided as an arg
    pinecone_key = args.pinecone_key
    pinecone_aws_region = args.pinecone_aws_region
    if not pinecone_aws_region: 
        # the free tier of pinecone only supports serverless
        # vector DBs in the US East 1 region. 
        pinecone_aws_region = 'us-east-1' 

    if not pinecone_key:
        key_path = pathlib.Path("~/.keys/pinecone.txt").expanduser()
        pinecone_key = open(key_path).read()

    if not input_dir or not output_dir or not dataset_metadata_path or not files_metadata_path:
        error_msg = "Set ROBOTO_INPUT_DIR, ROBOTO_OUTPUT_DIR and ROBOTO_DATASET_METADATA_CHANGESET_FILE, ROBOTO_FILE_METADATA_CHANGESET_FILE env variables."
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    # get dataset id
    invocation_id = load_env_var(RobotoEnvKey.InvocationId, strict=False)
    logger.info(f"{invocation_id=}")
    
    # If inside an invocation, get info for file-level tagging
    if invocation_id:
        # Setup and authorize HTTP client
        client = HttpClient(default_auth=SigV4AuthDecorator("execute-api"))
        service_url = load_env_var(RobotoEnvKey.RobotoServiceUrl)

        delegate = http_delegates.HttpDelegates.from_client(http=client, endpoint=service_url)
        invocation = actions.invocation.Invocation.from_id(invocation_id, delegate.invocations)
        dataset_id = invocation.data_source.data_source_id
        logger.info(f"{dataset_id}=")
        transaction_manager = TransactionManager(service_url, client)

        dataset = datasets.dataset.Dataset.from_id(dataset_id, dataset_delegate=delegate.datasets, file_delegate=delegate.files, transaction_manager=transaction_manager)
    else:
        dataset_id = "local_ds"
        dataset = None
    
    clip_model_name = args.clip_model
    if not clip_model_name: 
        clip_model_name = "openai/clip-vit-base-patch32"

    # setup CLIP model
    model = CLIPVisionModelWithProjection.from_pretrained(clip_model_name)
    processor = CLIPImageProcessor.from_pretrained(clip_model_name)

    # For now we conform to the HF interface and can guarantee this property exists
    projection_dim = model.visual_projection.out_features

    # setup Pinecone in serverless format
    pinecone_client = Pinecone(api_key=pinecone_key)
    index_name = args.pinecone_index_name
    index_list = pinecone_client.list_indexes() # pinecone client dict response
    # only expose indexes that are ready, and grab index if name provided and ready
    available_indexes = [idx['name'] if idx['status']['ready'] else None for idx in index_list]

    if index_name is None:
        index_name = "actiondb"
    if index_name not in available_indexes:
        #just create a new index tagged "action_db"
        pinecone_client.create_index(
                name=index_name,
                dimension=projection_dim, 
                metric="dotproduct",
                spec=ServerlessSpec(
                    region = pinecone_aws_region,
                    cloud = "aws"
                    ),
                )
    index = pinecone_client.Index(index_name)
  

    # get paths of all image files
    all_img_paths = []
    for img_ext in ["jpg", "JPG", "JPEG", "png", "PNG"]:
        all_img_paths.extend(glob(f"**/*.{img_ext}", root_dir=input_dir, recursive=True))

    if len(all_img_paths) == 0:
        logger.error("No JPEG files in input directory.")
        raise RuntimeError(f"No images in input dir.")
    
    pinecone_namespace = args.pinecone_namespace
    if pinecone_namespace is None:
        pinecone_namespace = dataset_id

    # check index stats beforehand for verifying upsertion later
    index_ns_record = index.describe_index_stats()['namespaces'].get(pinecone_namespace)
    if index_ns_record:
        vector_count_before = index_ns_record['vector_count']
    else:
        vector_count_before = 0
    
    # enumerate all image paths
    for img_path in all_img_paths:
        image = Image.open(input_dir / img_path)
        inputs = processor(images=image, return_tensors="pt", padding=True)
        outputs = model(**inputs)
        image_embedding = outputs.image_embeds


        index.upsert(
                vectors=[
                    {"id": img_path, "values": torch.squeeze(image_embedding).tolist()}
                    ],
                namespace=pinecone_namespace
                )
        
    # verify that index received upsert - this may take a while
    upserted = False
    time_waited = 0
    cycle_count = 0
    cycle_tokens = "-\\|/"
    while not upserted and time_waited < timeout:
        # add a little progress spinnning wheel
        print(f"Waiting to verify DB upsertion... {cycle_tokens[cycle_count]}", end="\r")

        index_ns_record = index.describe_index_stats()['namespaces'].get(pinecone_namespace)
        if index_ns_record:
            vector_count = index_ns_record['vector_count']
            if vector_count == vector_count_before + len(all_img_paths):
                upserted = True
        else:
            continue
        time_waited += wait_time 
        time.sleep(wait_time) 

    if not upserted:
        print("Warning: timeout exceeded without any record of vector uploads.")
    else:
        print(f"Success. Vectors stored to {index_name}:{pinecone_namespace}")
    
    # tag the dataset with associated Pinecone DB metadata
    metadata_file = args.dataset_metadata_path
    metadata_dict = {
            "put_fields": {
                "pinecone_index_name": index_name,
                "pinecone_namespace": pinecone_namespace
                }
            }
    # dump fields to dataset metadata
    with open(metadata_file, 'w') as f:
       json.dump(metadata_dict, f) 



if __name__ == "__main__":
     
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
        default=load_env_var(RobotoEnvKey.OutputDir)
    )
    parser.add_argument(
        "-d",
        "--dataset-metadata-path",
        dest="dataset_metadata_path",
        type=pathlib.Path,
        required=False,
        help="Path at which to save dataset-level metadata",
        default=load_env_var(RobotoEnvKey.DatasetMetadataChangesetFile)
    )
    parser.add_argument(
        "-f",
        "--files-metadata-path",
        dest="files_metadata_path",
        type=pathlib.Path,
        required=False,
        help="Path at which to save file-level metadata",
        default=load_env_var(RobotoEnvKey.FileMetadataChangesetFile)
    )
    parser.add_argument(
        "--pinecone-api-key",
        dest="pinecone_key",
        type=str,
        required=False,
        help="pinecone api key for vector DB service",
        default=os.getenv("ROBOTO_PARAM_PINECONE_API_KEY")
    )
    parser.add_argument(
        "--pinecone-aws-region",
        dest="pinecone_aws_region",
        type=str,
        required=False,
        help="AWS server region to host Pinecone DB in serverless format",
        default=os.getenv("ROBOTO_PARAM_PINECONE_AWS_REGION")
    )
    parser.add_argument(
        "--pinecone-index-name",
        dest="pinecone_index_name",
        type=str,
        required=False,
        help="name of specific Pinecone vector DB index",
        default=os.getenv("ROBOTO_PARAM_PINECONE_INDEX_NAME")
    )
    parser.add_argument(
        "--pinecone-namespace",
        dest="pinecone_namespace",
        type=str,
        required=False,
        help="namespace inside pinecone index into which to insert embeddings",
        default=os.getenv("ROBOTO_PARAM_PINECONE_NAMESPACE")
    )
    parser.add_argument(
        "--clip-model",
        dest="clip_model",
        type=str,
        required=False,
        help="Name of pretrained clip model from Huggingface archive to use for embedding images",
        default=os.getenv("ROBOTO_PARAM_CLIP_MODEL")
    )
    
    
    args = parser.parse_args()
    main(args)
