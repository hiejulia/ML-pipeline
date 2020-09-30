#
# Base image to be used by the build stage and the runtime image
#
FROM python:3 AS base

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y python3 \
    && rm -rf /var/lib/apt/lists/*
#
# Build stage: Builds and installs all the Python dependencies.
# This is used so that we don't need to bring the development packages
# to the runtime image, thus saving space.
#
FROM base AS builder

WORKDIR /build

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    netbase \
    git make \
    g++ \
    libboost-all-dev \
    zlib1g-dev \
    python3-dev

COPY requirements.txt .

RUN pip3 install --upgrade pip wheel
RUN mkdir /pythondeps
RUN pip3 wheel --wheel-dir=/pywheels -r ./requirements.txt

#
# Runtime image: This will run the application.
#
FROM base

LABEL maintainer="hien@nguyen"

# Install the built dependencies from the builder
COPY --from=builder /pywheels /pywheels
COPY requirements.txt ./
RUN pip3 install --no-index --find-links=/pywheels -r ./requirements.txt

# Copy the application source code
WORKDIR /project
COPY app.py basic_auth.py ./
COPY models/ ./models
COPY routes/ ./routes
COPY result_logging/ ./result_logging

# App user: this makes the container not run as root by default,
# which is good for security.
WORKDIR /tmp
RUN addgroup --gid 10101 --system appuser \
    && adduser --uid 10101 --system --group appuser
USER appuser:appuser

EXPOSE 5002
CMD python3 /project/app.py
