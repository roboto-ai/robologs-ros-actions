FROM robologs/robologs-ros2-iron-image:0.1

COPY requirements.runtime.txt ./
RUN python -m pip install --upgrade pip setuptools && python -m pip install -r requirements.runtime.txt

COPY src/db3_info/ ./db3_info

ENTRYPOINT [ "bash", "-c", "/db3_info/main.sh" ]
