FROM robologs/robologs-base-image:0.1
RUN ln -s /usr/bin/python3 /usr/bin/python

COPY requirements.runtime.txt ./
RUN python -m pip install --upgrade pip setuptools && python -m pip install -r requirements.runtime.txt

# Download the mcap CLI binary using wget
RUN wget https://github.com/foxglove/mcap/releases/download/releases%2Fmcap-cli%2Fv0.0.32/mcap-linux-amd64 -O /usr/local/bin/mcap

# Make the binary executable
RUN chmod +x /usr/local/bin/mcap

COPY requirements.runtime.txt ./
RUN python -m pip install --upgrade pip setuptools && python -m pip install -r requirements.runtime.txt

COPY src/ros_ingestion/ ./ros_ingestion

ENTRYPOINT [ "python", "-m", "ros_ingestion" ]
