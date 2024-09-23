FROM jodogne/orthanc:1.12.4
# or orthancteam/orthanc:24.8.3

FROM python:3.8 AS builder

COPY orthanc.json /etc/orthanc/orthanc.json

RUN apt-get update \
    && apt-get install -y --no-install-recommends g++ wget \
    && rm -rf /var/lib/apt/lists/*

COPY orthanc_requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels/ -r orthanc_requirements.txt

