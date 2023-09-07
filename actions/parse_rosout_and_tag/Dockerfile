ARG PYTHON_MAJOR=3
ARG PYTHON_MINOR=10
ARG OS_VARIANT=slim-bookworm
FROM --platform=linux/amd64 public.ecr.aws/docker/library/python:${PYTHON_MAJOR}.${PYTHON_MINOR}-${OS_VARIANT}

COPY requirements.runtime.txt ./
RUN python -m pip install --upgrade pip setuptools && python -m pip install -r requirements.runtime.txt

COPY src/parse_rosout_and_tag/ ./parse_rosout_and_tag

ENTRYPOINT [ "python", "-m", "parse_rosout_and_tag" ]
