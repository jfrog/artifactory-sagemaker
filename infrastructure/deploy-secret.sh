secret_name="sagemaker-poc-artifactory-details"
aws secretsmanager create-secret \
    --name ${secret_name} \
    --description "Secret with JFrog Artifactory and SageMaker integration values" \
    --secret-string "{\"username\":\"<USER>\",\"token\":\"<TOKEN>\",\"host\":\"<Artifactory host name>\",\"pypirepo\":\"sagemaker-pypi\",\"huggingfacerepo\":\"huggingface-remote\",\"huggingface-remote-repo\":\"https://<Artifactory host name>/artifactory/api/huggingfaceml/huggingface-remote\",\"huggingface-local-repo\":\"https://<Artifactory host name>/artifactory/api/huggingfaceml/huggingface-local\",\"huggingface-local-token\":\"<hf local token>\",\"huggingface-remote-token\":\"<hf remote token>\"}"
#Save the secret ARN and Name for the Lambda creation script