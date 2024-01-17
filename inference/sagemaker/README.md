# Inference

## Build inference image
```
docker build -t \
    myartifactory.jfrog.io/sagemaker-docker-virtual/sagemaker/inference-service:1.0_huggingface \
    --build-arg "ARTIFACTORY_DOCKER_REGISTRY=myartifactory.jfrog.io" \
    --build-arg "ARTIFACTORY_DOCKER_REPO=sagemaker-docker-virtual" .

docker push myartifactory.jfrog.io/sagemaker-docker-virtual/sagemaker/inference-service:1.0_huggingface
```