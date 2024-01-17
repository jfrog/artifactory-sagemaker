from sagemaker.estimator import Estimator
from datetime import datetime
import json

# The image URI of the training image (update the host and image name)
image_uri = "myartifactory.jfrog.io/sagemaker-docker-virtual/sagemaker/train:1.0_huggingface"

# Specify a security group and subnet (update names) for the VPC configuration for your training job
# Source: https://docs.aws.amazon.com/sagemaker/latest/dg/docker-containers-adapt-your-own-private-registry.html
security_groups = ["sg-111a1de1111cd11c1"]
subnets = ["subnet-1111c11111ec11f11"]

# Specify (update) the Amazon Resource Name (ARN) of an AWS Lambda function that provides access
# credentials to SageMaker
training_repository_credentials_provider_arn = 'arn:aws:lambda:eu-central-1:111111111111:function:sagemaker-poc-docker-registry-auth'

# Choose Vpc access mode to enable secured traffic in your own VPC
# Source: https://docs.aws.amazon.com/sagemaker/latest/dg/onboard-vpc.html
training_repository_access_mode = "Vpc"

# Set train job instance type
instance_type = "ml.m5.large"

# Set train job instance count
instance_count = 1

# Declare the maximum train job running time (in seconds)
max_run_time = 1800

# IAM ROLE ARN to enable the train job the right authorization (update)
role = 'arn:aws:iam::111111111111:role/service-role/AmazonSageMaker-ExecutionRole-20241111T111111'

# S3 uri location for the train job input data (input data should be uploaded prior to training)
input_path = 's3://my-s3-bucket/training-data-folder'

# Input_file: The dataset for train the model
input_file = "mnist.npz"

# The train and Test dataset
dataset = input_path + '/' + input_file

# The model repository id in Artifactory Huggingface local repository
repo_id = "mymodels/kares-tf"

# AWS secret containing Hugging Face credentials
# (Create secret prior to training)
secret_name = "sagemaker-poc-artifactory-details"

# Defined keys in AWS secret to store Hugging Face credentials
hf_local_repo = "huggingface-local-repo"
hf_local_token = "huggingface-local-token"

# Author
author = "SuperDS"

aws_region = 'eu-central-1'

# The new trained model revision
trained_revision = "v1"

# Unique train job name. Must be regular expression pattern: ^[a-zA-Z0-9](-*[a-zA-Z0-9]){0,62}
job_name = "train-tensorflow-" + str(datetime.timestamp(datetime.now())).replace('.', '-')

def json_encode_hyperparameters(hyperparameters):
    return {str(k): json.dumps(v) for (k, v) in hyperparameters.items()}

hyperparameters = json_encode_hyperparameters({'input_file': input_file,
                                               'repo_id': repo_id,
                                               'trained_revision': trained_revision,
                                               'hf_local_repo': hf_local_repo,
                                               'hf_local_token': hf_local_token,
                                               'author': author,
                                               'job_name': job_name,
                                               'dataset': dataset,
                                               'image_uri': image_uri,
                                               'secret_name': secret_name})
try:
    # A high level interface for SageMaker training that handle end-to-end
    # Amazon SageMaker training and deployment tasks.
    estimator = Estimator(
        image_uri=image_uri,
        role=role,
        subnets=subnets,
        security_group_ids=security_groups,
        training_repository_access_mode=training_repository_access_mode,
        training_repository_credentials_provider_arn=training_repository_credentials_provider_arn,
        instance_type=instance_type,
        instance_count=instance_count,
        hyperparameters=hyperparameters,
        max_run=max_run_time,
        environment={'AWS_DEFAULT_REGION': aws_region})

    # Execute the model train
    estimator.fit(
        inputs=input_path,
        job_name=job_name)

except Exception as e:
    print(f'error calling CreateTrainingJob operation: {e}')
else:
    print('Train job finish!')

