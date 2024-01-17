from sagemaker.model import Model

# Specify a security group and subnet for the VPC configuration for your real-time inference
# Source: https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms-containers-inference-private.html
security_groups = ["sg-11111111111111111"]
subnets = ["subnet-11111111111111111",
           "subnet-11111111111111112",
           "subnet-11111111111111113"]

# Specify the Amazon Resource Name (ARN) of an AWS Lambda function that provides access credentials to SageMaker
repository_credentials_provider_arn = 'arn:aws:lambda:eu-central-1:111111111111:function:sagemaker-poc-docker-registry-auth'

# Docker image that will be used to execute the model inference
deploy_image_uri = 'myartifactory.jfrog.io/sagemaker-docker-virtual/sagemaker/inference:1.0_huggingface'

# IAM ROLE ARN to enable the model inference the right authorization
aws_role = 'arn:aws:iam::111111111111:role/service-role/AmazonSageMaker-ExecutionRole-11111111T111111'

# Model inference instance type
instance_type = 'ml.m5.large'

# Model inference endpoint name for execution
endpoint_name = 'tensorflow-v2'

# Model inference instance count
instance_count = 1

# Region
aws_region = 'eu-central-1'

# AWS Secret with JFrog Huggingface endpoint and credentials
secret_name = 'sagemaker-poc-artifactory-details'
# AWS Secret keys
hf_local_repo = "huggingface-local-repo"
hf_local_token = "huggingface-local-token"

# JFrog Huggingface local repository id and model revision
revision = "v1"
repo_id = "mymodels/kares-tf"

# Directory of the model download location in inference container. See Dockerfile
model_dir = "/opt/ml/model"

# Model initialization
model = Model(
    image_uri=deploy_image_uri,
    role=aws_role,
    name="tensorflow-v2",
    vpc_config={'Subnets': subnets, 'SecurityGroupIds': security_groups},
    image_config={'RepositoryAccessMode': 'Vpc',
                  'RepositoryAuthConfig': {"RepositoryCredentialsProviderArn": repository_credentials_provider_arn}},
    env={'AWS_DEFAULT_REGION': aws_region,
         'JF_SECRET_NAME': secret_name,
         'JF_SECRET_HF_LOCAL_REPO': hf_local_repo,
         'JF_SECRET_HF_LOCAL_TOKEN': hf_local_token,
         'JF_REPO_ID': repo_id,
         'JF_REVISION': revision,
         'JF_MODEL_DIR': model_dir})

# Model inference deployment
model_predictor = model.deploy(
    initial_instance_count=instance_count,
    instance_type=instance_type,
    endpoint_name=endpoint_name,
)
