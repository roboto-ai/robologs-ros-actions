import cv2
import os
import argparse
import glob
import pathlib
from roboto.domain import actions

def extract_frames(video_path, output_folder, frame_rate, image_format):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video file {video_path}")
        return

    video_frame_rate = cap.get(cv2.CAP_PROP_FPS)
    skip_rate = max(1, int(video_frame_rate / frame_rate)) if frame_rate else 1

    count = 0
    saved_count = 0

    video_name = os.path.splitext(os.path.basename(video_path))[0]
    video_output_folder = os.path.join(output_folder, video_name)
    os.makedirs(video_output_folder, exist_ok=True)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if count % skip_rate == 0:
            frame_number = str(saved_count).zfill(7)
            output_filename = os.path.join(video_output_folder, f"{video_name}_frame_{frame_number}.{image_format}")
            cv2.imwrite(output_filename, frame)
            saved_count += 1

        count += 1

    cap.release()
    print(f"Finished extracting frames from {video_path}")

def process_videos(input_folder, output_folder, frame_rate, image_format):
    supported_formats = ['mp4', 'avi', 'mkv', 'mov']
    for video_format in supported_formats:
        for video_file in glob.glob(os.path.join(input_folder, f"*.{video_format}")):
            print(f"Processing {video_file}...")
            extract_frames(video_file, output_folder, frame_rate, image_format)

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input-dir", dest="input_dir", type=pathlib.Path, required=False, help="Directory containing input files to process", default=os.environ.get(actions.InvocationEnvVar.InputDir.value))
parser.add_argument("-o", "--output-dir", dest="output_dir", type=pathlib.Path, required=False, help="Directory to which to write any output files to be uploaded", default=os.environ.get(actions.InvocationEnvVar.OutputDir.value))
parser.add_argument("--frame_rate", type=float, required=False, help="Frame rate at which to extract images", default=os.environ.get("ROBOTO_PARAM_FRAME_RATE"))
parser.add_argument("--image_format", type=str, required=False, help="Format of output images (png or jpg)", default=os.environ.get("ROBOTO_PARAM_IMAGE_FORMAT", "jpg"))

args = parser.parse_args()
process_videos(args.input_dir, args.output_dir, args.frame_rate, args.image_format.lower())
