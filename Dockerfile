FROM python:3.9-slim-buster

RUN apt-get -y update
RUN pip3 install --upgrade pip
RUN python3 -m pip install --upgrade setuptools

COPY ./src /opt/cti-stats-collector
WORKDIR /opt/cti-stats-collector

RUN pip3 install -r requirements.txt
RUN touch /opt/cti-stats-collector/collector.log
RUN ln -sf /dev/stdout /opt/cti-stats-collector/collector.log \
    && ln -sf /dev/stderr /opt/cti-stats-collector/collector.log

VOLUME [ "./config" ]

WORKDIR /opt/cti-stats-collector/
CMD ["python", "collector.py"]