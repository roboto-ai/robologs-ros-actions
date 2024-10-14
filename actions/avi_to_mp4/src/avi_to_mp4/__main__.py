import argparse
import os
import pathlib
import subprocess

from roboto.domain import actions


def convert_avi_to_mp4(
    avi_file_path: str, 
    input_base_dir: str, 
    output_base_dir: str, 
    bitrate: str, 
    frame_rate: str, 
    resolution: str, 
    crf: str, 
    preset: str
) -> None:
    """
    Converts an AVI or MKV file to MP4 format using ffmpeg.

    Parameters:
        avi_file_path (str): Full path to the AVI or MKV file.
        input_base_dir (str): Base directory of the input files.
        output_base_dir (str): Base directory where the output MP4 will be saved.
        bitrate (str): Video bitrate (e.g., '1M').
        frame_rate (str): Frame rate of the video (e.g., '24').
        resolution (str): Video resolution (e.g., '1280x720').
        crf (str): Constant Rate Factor for encoding quality (e.g., '23').
        preset (str): Encoding preset (e.g., 'slow').
    """
    relative_path = os.path.relpath(avi_file_path, input_base_dir)
    relative_mp4_path = os.path.splitext(relative_path)[0] + '.mp4'
    mp4_file_path = os.path.join(output_base_dir, relative_mp4_path)

    os.makedirs(os.path.dirname(mp4_file_path), exist_ok=True)

    ffmpeg_command = ["ffmpeg", "-i", avi_file_path]
    
    if bitrate:
        ffmpeg_command.extend(["-b:v", bitrate])
    if frame_rate:
        ffmpeg_command.extend(["-r", frame_rate])
    if resolution:
        ffmpeg_command.extend(["-s", resolution])
    if crf:
        ffmpeg_command.extend(["-crf", crf])
    if preset:
        ffmpeg_command.extend(["-preset", preset])

    ffmpeg_command.append(mp4_file_path)
    subprocess.run(ffmpeg_command, check=True)


def main(args: argparse.Namespace) -> None:
    """
    Main function to traverse input directory and convert AVI/MKV files to MP4.
    
    Parameters:
        args (argparse.Namespace): Parsed command-line arguments.
    """
    input_dir = str(args.input_dir)
    output_dir = str(args.output_dir)

    for root, _, files in os.walk(input_dir):
        for filename in files:
            if filename.endswith((".avi", ".mkv")):
                avi_file_path = os.path.join(root, filename)
                convert_avi_to_mp4(
                    avi_file_path,
                    input_dir,
                    output_dir,
                    args.bitrate,
                    args.frame_rate,
                    args.resolution,
                    args.crf,
                    args.preset
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert AVI/MKV files to MP4 format using ffmpeg.")
    
    parser.add_argument(
        "-i", "--input-dir", 
        dest="input_dir", 
        type=pathlib.Path, 
        required=False, 
        help="Directory containing input files to process", 
        default=os.getenv("ROBOTO_INPUT_DIR")
    )
    parser.add_argument(
        "-o", "--output-dir", 
        dest="output_dir", 
        type=pathlib.Path, 
        required=False, 
        help="Directory to save converted MP4 files", 
        default=os.getenv("ROBOTO_OUTPUT_DIR")
    )

    parser.add_argument("--bitrate", type=str, help="Set video bitrate (e.g., '1M')", default=os.environ.get("ROBOTO_PARAM_BITRATE"))
    parser.add_argument("--frame_rate", type=str, help="Set video frame rate (e.g., '24')", default=os.environ.get("ROBOTO_PARAM_FRAME_RATE"))
    parser.add_argument("--resolution", type=str, help="Set video resolution (e.g., '1280x720')", default=os.environ.get("ROBOTO_PARAM_RESOLUTION"))
    parser.add_argument("--crf", type=str, help="Set Constant Rate Factor for encoding quality (e.g., '23')", default=os.environ.get("ROBOTO_PARAM_CRF"))
    parser.add_argument("--preset", type=str, help="Set encoding preset (e.g., 'slow')", default=os.environ.get("ROBOTO_PARAM_PRESET"))

    args = parser.parse_args()
    main(args)
