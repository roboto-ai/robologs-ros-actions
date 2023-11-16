import argparse
import os
import pathlib
import subprocess

from roboto.domain import actions

def convert_avi_to_mp4(avi_file_path, output_dir, bitrate, frame_rate, resolution, crf, preset):
    mp4_file_path = os.path.join(output_dir, os.path.splitext(os.path.basename(avi_file_path))[0] + '.mp4')
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
    subprocess.run(ffmpeg_command)

def main(args: argparse.Namespace) -> None:
    input_dir = args.input_dir
    output_dir = args.output_dir
    
    for filename in os.listdir(input_dir):
        if filename.endswith(".avi"):
            convert_avi_to_mp4(
                os.path.join(input_dir, filename), 
                output_dir,
                args.bitrate,
                args.frame_rate,
                args.resolution,
                args.crf,
                args.preset
            )
    
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input-dir", dest="input_dir", type=pathlib.Path, required=False, help="Directory containing input files to process", default=os.environ.get(actions.InvocationEnvVar.InputDir.value))
parser.add_argument("-o", "--output-dir", dest="output_dir", type=pathlib.Path, required=False, help="Directory to which to write any output files to be uploaded", default=os.environ.get(actions.InvocationEnvVar.OutputDir.value))

# Adding new arguments
parser.add_argument("--bitrate", type=str, help="Set video bitrate (e.g., '1M')", default=os.environ.get("ROBOTO_PARAM_BITRATE"))
parser.add_argument("--frame_rate", type=str, help="Set video frame rate (e.g., '24')", default=os.environ.get("ROBOTO_PARAM_FRAME_RATE"))
parser.add_argument("--resolution", type=str, help="Set video resolution (e.g., '1280x720')", default=os.environ.get("ROBOTO_PARAM_RESOLUTION"))
parser.add_argument("--crf", type=str, help="Set the Constant Rate Factor (e.g., '23')", default=os.environ.get("ROBOTO_PARAM_CRF"))
parser.add_argument("--preset", type=str, help="Set encoding preset (e.g., 'slow')", default=os.environ.get("ROBOTO_PARAM_PRESET"))

args = parser.parse_args()
main(args)
