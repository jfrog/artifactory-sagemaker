# Artifactory server/registry and repo for resolving Docker images
ARG ARTIFACTORY_DOCKER_REGISTRY
ARG ARTIFACTORY_DOCKER_REPO

# Download an open source TensorFlow Docker image to use as the Base Image
FROM ${ARTIFACTORY_DOCKER_REGISTRY}/${ARTIFACTORY_DOCKER_REPO}/tensorflow/tensorflow:latest-gpu-jupyter

# Install sagemaker-training toolkit that contains the common functionality
# necessary to create a container compatible with SageMaker and the Python SDK.
COPY requirements.txt /opt/ml/code/

# Utilize Artifactory private remote pypi repo to resolve python dependencies
# Note: The private repository credentials are passed in as a build secret in the
#    form of a pip configuration file with the target location equal to the
#    expected location of a pip configuration file in the container.
#
#    Ensure the source file 'pip.conf' in this project with the appropriate
#    index-url and credentials.
RUN --mount=type=secret,id=pipconfig,target=/etc/pip.conf \
    pip install -r /opt/ml/code/requirements.txt

# Copies the training code inside the container
COPY train.py /opt/ml/code/train.py

# Defines train.py as script entrypoint
ENV SAGEMAKER_PROGRAM train.py
