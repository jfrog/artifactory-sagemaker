ARG ARTIFACTORY_DOCKER_REGISTRY
ARG ARTIFACTORY_DOCKER_REPO

# For demo purposes, the training image is used as a base image since it already contains
# required dependencies
FROM ${ARTIFACTORY_DOCKER_REGISTRY}/${ARTIFACTORY_DOCKER_REPO}/sagemaker/train:1.0_huggingface

RUN apt update && apt install openjdk-17-jdk -y

# For AWS sagemaker as the Model directory
RUN mkdir -p /opt/ml/model

# Copy the default custom service file to handle incoming data and inference requests
RUN mkdir -p /home/model-server/
COPY inference.py /home/model-server/inference.py
COPY entrypoint.py /usr/local/bin/entrypoint.py

RUN chmod +x /usr/local/bin/entrypoint.py

# Define an entrypoint script for the Docker image
ENTRYPOINT ["python", "/usr/local/bin/entrypoint.py"]