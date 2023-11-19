from sagemaker.estimator import Estimator



#The image URI that was build in the build train container phase
image_uri = "<docker image uri>"

#Specify a security group and subnet for the VPC configuration for your training job
#Source: https://docs.aws.amazon.com/sagemaker/latest/dg/docker-containers-adapt-your-own-private-registry.html
security_groups = ["<security group>"]
subnets = ["<subnet1>,<subnet2>,..."]
#specify the Amazon Resource Name (ARN) of an AWS Lambda function that provides access credentials to SageMaker
training_repository_credentials_provider_arn = '<lambda function arn>'
#Choose Vpc access mode to enable secured traffic in your own VPC
#Source: https://docs.aws.amazon.com/sagemaker/latest/dg/onboard-vpc.html
training_repository_access_mode = "Vpc"
#Set train job instance type
instance_type = "ml.m5.large"
#Set train job instance count
instance_count = 1
#Declare the maximum train job running time
max_run_time = 1800
#Set the s3 bucket and location to save the model after train successfully.
output_path = '<s3 uri>'
#The IAM ROLE ARN to enable the train job the right authorization
role = 'iam role arn'
#Set the S3 uri location for the train job input data
input_path = '<s3 uri>'

try:
    #A high level interface for SageMaker training that handle end-to-end Amazon SageMaker training and deployment tasks.
    estimator = Estimator(
        image_uri=image_uri,
        role=role,
        subnets=subnets,
        security_group_ids=security_groups,
        training_repository_access_mode=training_repository_access_mode,
        training_repository_credentials_provider_arn=training_repository_credentials_provider_arn,
        instance_type=instance_type,
        instance_count=instance_count,
        hyperparameters = {'input_file': 'mnist.npz'},
        output_path=output_path,
        max_run=max_run_time)

    #Set unique train job name
    job_name = "<Job name>"
    
    # Execute the model train
    estimator.fit(
       inputs=input_path,
       job_name=job_name)

except Exception as e:
    print(f'error calling CreateTrainingJob operation: {e}')
else:
    print('Train job finish!')

