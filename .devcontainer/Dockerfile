FROM mcr.microsoft.com/devcontainers/python:3.13

# Install additional system packages required by Home Assistant
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        ffmpeg \
        libturbojpeg0 \
        libpcap-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
