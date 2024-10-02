# Stage 1: Build the Python environment and dependencies
FROM python:3.8 AS builder

# Install necessary packages for Python
RUN apt-get update \
    && apt-get install -y --no-install-recommends g++ wget \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies (related to Orthanc)
COPY docker/orthanc_requirements.txt orthanc_requirements.txt
RUN pip wheel --no-cache-dir --wheel-dir /wheels/ -r orthanc_requirements.txt

# Stage 2: Set up the main Python environment
FROM python:3.8-slim AS python-env

# Set working directory for the app
WORKDIR /app

# Install additional packages required for your application
RUN apt-get update && apt-get install -y --no-install-recommends \
    dcmtk python3-sklearn-lib git wget unzip \
    && rm -rf /var/lib/apt/lists/*

# Copy Python wheels from the builder stage and install them
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels/

# Install the model and server code
ARG MODEL_COMMIT=v0.13.0
RUN pip install --no-cache-dir --disable-pip-version-check \
    git+https://github.com/reginabarzilaygroup/Mirai.git@${MODEL_COMMIT}

ARG ARK_COMMIT=v0.8.0
RUN git clone https://github.com/reginabarzilaygroup/ark.git
RUN cd ark && git checkout ${ARK_COMMIT} \
    && pip install --no-cache-dir --disable-pip-version-check -e .

# Download trained model weights
RUN mirai-predict --dry-run

# Expose the necessary ports for the app
EXPOSE 5000 8000

# Environment variables
ENV LOG_LEVEL="INFO"
ENV ARK_THREADS=4

# Stage 3: Orthanc setup
FROM jodogne/orthanc:1.12.4 AS orthanc

# Copy the custom Orthanc configuration file
COPY docker/orthanc.json /etc/orthanc/orthanc.json

# Expose the Orthanc ports
EXPOSE 8042 11112

# Stage 4: Final stage combining Python app and Orthanc
FROM python:3.8-slim

# Copy the Python app from the python-env stage
COPY --from=python-env /app /app

# Copy Orthanc from the orthanc stage
COPY --from=orthanc /etc/orthanc /etc/orthanc

# Expose all necessary ports
EXPOSE 5000 8000

# Set environment variables
ENV LOG_LEVEL="INFO"
ENV ARK_THREADS=4

# Start both Orthanc and the Python app
CMD ["Orthanc /etc/orthanc/orthanc.json & python /app/ark/orthanc/rest_listener.py"]
