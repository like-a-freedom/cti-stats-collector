FROM python:3.9.9-slim-buster

RUN apt-get -y update
RUN apt-get install -y gcc musl-dev
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --upgrade setuptools

COPY ./src /opt/cti-stats-storage
WORKDIR /opt/cti-stats-storage

RUN pip3 install -r requirements.txt
RUN touch /opt/cti-stats-storage/storage.log
RUN ln -sf /dev/stdout /opt/cti-stats-storage/storage.log \
    && ln -sf /dev/stderr /opt/cti-stats-storage/storage.log

CMD ["uvicorn", "api:api", "--host", "0.0.0.0", "--port", "80"]