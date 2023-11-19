#Download an open source TensorFlow Docker image
ARG ARTIFACTORY_DOCKER_REGISTRY
FROM ${ARTIFACTORY_DOCKER_REGISTRY}/sagemaker-docker-virtual/tensorflow/tensorflow:latest-gpu-jupyter

# Setup pypi index url - for dependency resolution
ARG PYPI_INDEX_URL
RUN pip config --global set global.index-url "${PYPI_INDEX_URL}"
# Install sagemaker-training toolkit that contains the common functionality necessary to create a container compatible with SageMaker and the Python SDK.
RUN pip3 install sagemaker-training numpy sagemaker boto3 argparse six

# Copies the training code inside the container
COPY train_load_from_s3.py /opt/ml/code/train.py

# Defines train.py as script entrypoint
ENV SAGEMAKER_PROGRAM train.py
