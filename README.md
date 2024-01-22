# Artifactory-Sagemaker

Demo to implement the integration between JFrog Artifactory and AWS Sagemaker

## Directory Contents

<details>
  <summary>dev

Includes files related to Notebooks created within SageMaker or launched from SageMaker console
</summary>

***

**Notebook subdirectory** - <i>for use when launching a notebook instance from the SageMaker console</i>

- `lifecycle_configuration.sh`
   
   Code of the lifecycle configuration script to launch a sagemaker Notebook instance

***
 
**Studio subdirectory** - <i>for use when working within SageMaker Studio Classic</i>

- `example.ipynb`
  
   Jupyter notebook with commands to demonstrate the following Artifactory and Sagemaker integrations after creating the 
notebook in an environment started with the lifecycle configuration script:
   1. JFrog CLI
   2. Artifactory PyPI virtual repository
   3. Artifactory HuggingFace ML remote repository


- `lifecycle_configuration.sh`
  
   Code of the lifecycle configuration script to launch a sagemaker studio lab IDE 

</details>

***

<details>
<summary>inference

Includes files related to deploying a model for real-time inference including
retrieving a custom model from an Artifactory HuggingFace ML repository and creating a custom Docker image to
launch with the SageMaker inference service
</summary>

***

**sagemaker subdirectory**

  - `Dockerfile`
  
    Dockerfile to build a custom image for inference
  
    Example `docker` commands to log in to the Artifactory Docker registry and then to build and push the 
inference image to Artifactory:
  
    ```
    docker login myartifactory.jfrog.io -u <USER> -p <TOKEN>
    
    docker build -t \
      myartifactory.jfrog.io/sagemaker-docker-virtual/sagemaker/inference-service:1.0_huggingface \
      --build-arg "ARTIFACTORY_DOCKER_REGISTRY=myartifactory.jfrog.io" \
      --build-arg "ARTIFACTORY_DOCKER_REPO=sagemaker-docker-virtual" .

    docker push myartifactory.jfrog.io/sagemaker-docker-virtual/sagemaker/inference-service:1.0_huggingface
    ```
  

  - `entrypoint.py`
  
    Entrypoint script used in the custom Docker image to set up the inference handler service
  

  - `inference.py`
  
    Code included in the custom Docker image to handle inference using a custom Hugging Face ML model
  


***

- `deploy-model.py`

  Code to deploy the trained model as a SageMaker real-time inference
  

- `test-inference.py`

  Code to test the deployed SageMaker real-time inference
  

</details>

***

<details>
  <summary>infrastructure

Includes files related to setting up the AWS secret and Lambda required for the
use of Artifactory within a SageMaker VPC environment
</summary>

***

- `deploy-lambda.sh`
- `deploy-secret.sh`
- `lambda_function.py`

</details>

***

<details>
  <summary>train

Includes files related to creating and running a custom Docker image to
train and store a model in Artifactory
</summary>

***

- `Dockerfile`

  Dockerfile to build a model train image

  Example `docker` commands to log in to the Artifactory Docker registry and then to build and push the training image
to Artifactory:
  ```
  docker login myartifactory.jfrog.io -u <USER> -p <TOKEN>

  docker build -t \
    myartifactory.jfrog.io/sagemaker-docker-virtual/sagemaker/train:1.0_huggingface \
    --secret id=pipconfig,src=pip.conf \
    --build-arg "ARTIFACTORY_DOCKER_REGISTRY=myartifactory.jfrog.io" \
    --build-arg "ARTIFACTORY_DOCKER_REPO=sagemaker-docker-virtual" .

    docker push myartifactory.jfrog.io/sagemaker-docker-virtual/sagemaker/train:1.0_huggingface
  ```
  

- `pip.conf`
  
  File used to configure the Artifactory PyPI repository for use during the Python package installation section of the 
Docker image build (used as a [Docker build secret](https://docs.docker.com/build/building/secrets/))
  

- `requirements.txt`
  
  Python package requirements for use during the custom Docker image build
  
  These requirements satisfy everything 
needed for both the <i>train.py</i> and <i>inference.py</i> scripts (both are combined to 
simplify the demo)
  

- `run-train-job.py`

  Code to create and execute SageMaker train job using a custom Docker image


- `train.py`

  Model train code that the SageMaker train job will execute



</details>
