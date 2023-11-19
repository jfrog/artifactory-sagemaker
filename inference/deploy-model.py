from sagemaker.model import Model
from sagemaker.predictor import Predictor

#Specify a security group and subnet for the VPC configuration for your real-time inference
#Source: https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms-containers-inference-private.html
security_groups = [<security group/s>]
subnets = [<subnet1>,<subnet2>]
#specify the Amazon Resource Name (ARN) of an AWS Lambda function that provides access credentials to SageMaker
repository_credentials_provider_arn = '<lambda function arn>'
#The docker image that will be used to execute the model inference
deploy_image_uri = '<docker image uri>'
#The model file location in s3
model_uri = "<s3 uri>"
#The IAM ROLE ARN to enable the model inference the right authorization
aws_role = 'iam role arn'
#Set model inference instance type
instance_type = 'ml.m5.2xlarge'
#Model inference endpoint name for execution
endpoint_name = 'tensorflow-v1'
#Set model inference instance count
instance_count = 1

#Model initilization
model = Model(
    image_uri=deploy_image_uri,
    model_data=model_uri,
    role=aws_role,
    predictor_cls=Predictor,
    name="tensorflow",
    vpc_config={'Subnets': subnets, 'SecurityGroupIds': security_groups},
    image_config={'RepositoryAccessMode': 'Vpc', 'RepositoryAuthConfig': {"RepositoryCredentialsProviderArn": repository_credentials_provider_arn}},
)


#Model inference deployment
model_predictor = model.deploy(
    initial_instance_count=instance_count,
    instance_type=instance_type,
    predictor_cls=Predictor,
    endpoint_name=endpoint_name,
)
