FROM robologs/robologs-base-image:0.1

# Install other requirements
COPY requirements.runtime.txt ./
RUN /usr/bin/python3 -m pip install --upgrade pip setuptools && /usr/bin/python3 -m pip install -r requirements.runtime.txt

COPY src/merge_rosbags/ ./merge_rosbags

ENTRYPOINT [ "python3", "-m", "merge_rosbags" ]
