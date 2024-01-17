# Create zip deployment from the source code
# Reference:https://docs.aws.amazon.com/lambda/latest/dg/python-package.html
mkdir package
pip install --target ./package requests
cd package
zip -r ../sagemaker-poc-docker-registry-auth.zip .
cd ..
zip sagemaker-poc-docker-registry-auth.zip lambda_function.py
# Create IAM execution role
region="eu-central-1"
account_id="111111111111"
lambda_name="sagemaker-poc-docker-registry-auth-test"
secret_arn="arn:aws:secretsmanager:eu-central-1:111111111111:secret:sagemaker-poc-artifactory-details-ezmXU8"
role_name="sagemaker-poc-docker-registry-auth-lambda-ex"
policy_name="sagemaker-poc-docker-registry-auth-lambda-policy"
cat >lambda-policy.json <<EOF
{
     "Version": "2012-10-17",
     "Statement": [
        {
            "Effect": "Allow",
            "Action": "logs:CreateLogGroup",
            "Resource": "arn:aws:logs:${region}:${account_id}:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream",
                "logs:PutLogEvents",
              "secretsmanager:GetSecretValue"
          ],
          "Resource": [
              "arn:aws:logs:${region}:${account_id}:log-group:/aws/lambda/${lambda_name}:*",
              "${secret_arn}"
          ]
      }
     ]
}
EOF

aws iam create-policy --policy-name ${policy_name} --policy-document file://lambda-policy.json 2>&1 > /dev/null

cat >trust-policy.json <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

aws iam create-role --role-name ${role_name} --assume-role-policy-document file://trust-policy.json 2>&1 > /dev/null
aws iam attach-role-policy --role-name ${role_name} --policy-arn arn:aws:iam::${account_id}:policy/${policy_name} 2>&1 > /dev/null
# Wait for the role creation before lambda function creation
sleep 60
aws lambda create-function  --function-name ${lambda_name} \
--runtime python3.11 --handler lambda_function.lambda_handler \
--role arn:aws:iam::${account_id}:role/${role_name} \
--zip-file fileb://sagemaker-poc-docker-registry-auth.zip 2>&1 > /dev/null
# Wait for the lambda function creation before update-function-configuration
sleep 60
# Update the secret cache layer. E.G> the layer for the eu-central-1 region
# https://docs.aws.amazon.com/systems-manager/latest/userguide/ps-integration-lambda-extensions.html
layerVersion=4
layerARN="arn:aws:lambda:eu-central-1:187925254637:layer:AWS-Parameters-and-Secrets-Lambda-Extension:${layerVersion}"
aws lambda update-function-configuration \
    --function-name ${lambda_name} \
    --layers ${layerARN} 2>&1 > /dev/null
# Wait for the lambda function update-function-configuration layer before update-function-configuration environment
sleep 60
# Add the environment variables to the lambda function
secret_name="sagemaker-poc-artifactory-details"
port="2773"
aws lambda update-function-configuration --function-name ${lambda_name} --environment "Variables={"JF_SECRET_NAME"=${secret_name}, "PARAMETERS_SECRETS_EXTENSION_HTTP_PORT"=${port}}" 2>&1 > /dev/null

#Note: Add to the sagemaker execution role the permission to execute this Lambda function.
#E.G.
#        {
 #            "Action": [
 #                "lambda:InvokeFunction"
 #            ],
 #            "Effect": "Allow",
 #            "Resource": [
 #                "arn:aws:lambda:${region}:${account_id}:function:${lambda_name}"
 #            ]
 #        }
