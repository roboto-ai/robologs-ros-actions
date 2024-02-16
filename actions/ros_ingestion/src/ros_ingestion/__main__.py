import argparse
import os
import pathlib

from roboto.domain import actions


def main(args: argparse.Namespace) -> None:
    print("Hello World!")
    print(f"Contents of input directory {args.input_dir}:")
    for file in args.input_dir.iterdir():
        print(f"  {file}")

    print(f"Output directory: {args.output_dir}")


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

args = parser.parse_args()
main(args)
