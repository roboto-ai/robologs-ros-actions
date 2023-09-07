FROM robologs/robologs-base-image:0.1

# Download the mcap CLI binary using wget
RUN wget https://github.com/foxglove/mcap/releases/download/releases%2Fmcap-cli%2Fv0.0.32/mcap-linux-amd64 -O /usr/local/bin/mcap

# Make the binary executable
RUN chmod +x /usr/local/bin/mcap

COPY src/main.sh /main.sh

CMD [ "/main.sh" ]
