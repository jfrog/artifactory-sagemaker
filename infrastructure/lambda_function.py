import json
import sys, os
import requests


print('Loading function sagemaker-poc-docker-registry-auth')

def lambda_handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    try:
        headers = {"X-Aws-Parameters-Secrets-Token": os.environ.get('AWS_SESSION_TOKEN')}
        secrets_extension_http_port = os.environ.get('PARAMETERS_SECRETS_EXTENSION_HTTP_PORT')
        secret_name = os.environ.get('JF_SECRET_NAME')
        secrets_extension_endpoint = "http://localhost:" + \
                                     str(secrets_extension_http_port) + \
                                     "/secretsmanager/get?secretId=" + \
                                     secret_name
        r = requests.get(secrets_extension_endpoint, headers=headers)
        secret = json.loads(json.loads(r.text)["SecretString"]) # load the Secrets Manager response into a Python dictionary, access the secret
        username = secret['username']
        password = secret['token']
        response = {
            "Credentials": {"Username": username, "Password": password}
        }
        return response
    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        raise e

