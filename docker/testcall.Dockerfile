FROM python:3.8 AS builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends g++ wget \
    && rm -rf /var/lib/apt/lists/*

RUN pip install requests

COPY orthanc/testcall.py testcall.py

ENTRYPOINT [ "python", "testcall.py" ]