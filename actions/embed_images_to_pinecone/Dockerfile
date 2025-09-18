FROM robologs/robologs-base-image:0.1

# Install other requirements
COPY requirements.runtime.txt ./
RUN /usr/bin/python3 -m pip install --upgrade pip setuptools && /usr/bin/python3 -m pip install -r requirements.runtime.txt

RUN apt-get update && apt install -y git
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install git+https://github.com/roboto-ai/rosbags-fork.git

COPY src/embed_images_to_pinecone/ ./embed_images_to_pinecone

ENTRYPOINT [ "python3", "-m", "embed_images_to_pinecone" ]
