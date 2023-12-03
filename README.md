# Artifactory-Sagemaker

## Demo to implement the integration between JFrog Artifactory to AWS Sagemaker.


## dev directory
### Notebook subdirectory
#### lifecycle_configuration.sh
##### Code of the lifecycle configuration script to launch a sagemaker Notebook instance.

### Studio subdirectory
#### lifecycle_configuration.sh
###### Code of the lifecycle configuration script to launch a sagemaker studio lab IDE 

#### example.ipynb
###### Jupiter notebook with comands to the set Artifactory and Sagemaker following integration:
###### 1. JFrog cli
###### 2. Artifactory Pypi virtual repository
###### 3. Artifactory Huggingface remote repository 

## train directory
#### Dockerfile
###### Dockerfile to build a model train image.
#### Build:
```agsl
docker login <Artifactory url> -u <USER> -p <TOKEN>

docker build -t <IMAGE NAME:TAG> --build-arg "PYPI_INDEX_URL=<Artifactory url><pypi virtual repo path and credentiales>" --build-arg "ARTIFACTORY_DOCKER_REGISTRY=<artifactory docker registry name>" .

```
#### train.py
###### model train code that the Sagemaker train job will execute.

#### training-job-private-docker-registry.py
###### Code to create and execute Sagemaker train job using the Docker image we build.

## inference directory
#### deploy-model.py
###### Code to deploy the trained model as a Sagemaker realtime inference.

####  test-inference.py
###### Code to test the deployd Sagemaker realtime inference.
