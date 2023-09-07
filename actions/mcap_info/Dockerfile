FROM robologs/robologs-base-image:0.1

# Download the mcap CLI binary using wget
RUN wget https://github.com/foxglove/mcap/releases/download/releases%2Fmcap-cli%2Fv0.0.32/mcap-linux-amd64 -O /usr/local/bin/mcap

# Make the binary executable
RUN chmod +x /usr/local/bin/mcap

COPY requirements.runtime.txt ./
RUN python3 -m pip install --upgrade pip setuptools && python3 -m pip install -r requirements.runtime.txt

COPY src/mcap_info/ ./mcap_info

ENTRYPOINT [ "python3", "-m", "mcap_info" ]
