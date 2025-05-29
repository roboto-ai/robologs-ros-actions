FROM --platform=linux/amd64 ubuntu:22.04

RUN \
apt-get update && \
apt-get install unzip xz-utils -y && \
rm -rf /var/lib/apt/lists/*

COPY src/main.sh /main.sh

CMD [ "/main.sh" ]
