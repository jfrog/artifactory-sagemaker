import os

# Disable irrelevant warning messages
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'

import tensorflow as tf
import numpy as np
import argparse
from huggingface_hub import HfApi
import boto3
from botocore.exceptions import ClientError
import json
from datetime import datetime

# Load npz file from local folder
def load_data(path):
    with np.load(path) as f:
        x_train, y_train = f['x_train'], f['y_train']
        x_test, y_test = f['x_test'], f['y_test']
        return (x_train, y_train), (x_test, y_test)

def get_secret(secret_name):
    _secret_name = secret_name
    # Create a Secrets Manager client
    session = boto3.session.Session()
    region_name = session.region_name
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=_secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']
    return json.loads(secret)

def upload_model(model_save_dir, repo_id, repo_type, trained_revision, hf_local_repo, hf_local_token):
    api = HfApi(endpoint=hf_local_repo, token=hf_local_token)
    if trained_revision:
        api.upload_folder(folder_path=model_save_dir,
                          repo_id=repo_id,
                          repo_type=repo_type,
                          revision=trained_revision)
    else:
        api.upload_folder(folder_path=model_save_dir, repo_id=repo_id, repo_type=repo_type)
    print("Info: Model: {} , revision: {} upload successfully.".format(repo_id, trained_revision))

def generate_readme(author, repo_id, revision, job_name, dataset, image_uri, path):
    # Generate new revision and upload trained model back to Artifactory
    lines = ["# Author: " + author,
             "# Timestamp: " + str(datetime.now()),
             "# Model: " + repo_id,
             "# Revision: " + revision,
             "# Job name: " + job_name,
             "# Train and Test Dataset: " + dataset,
             "# Train Image: " + image_uri]
    readme_file = "README.md"
    with open(path + '/' + readme_file, "w") as f:
        f.write('\n'.join(lines))
        f.close()

if __name__ == '__main__':
    # Parse training job input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--training', type=str, default=os.environ.get('SM_CHANNEL_TRAINING'))
    parser.add_argument('--input_file', type=str)
    parser.add_argument('--repo_id', type=str)
    parser.add_argument('--trained_revision', type=str)
    parser.add_argument('--hf_local_repo', type=str)
    parser.add_argument('--hf_local_token', type=str)
    parser.add_argument('--author', type=str)
    parser.add_argument('--job_name', type=str)
    parser.add_argument('--dataset', type=str)
    parser.add_argument('--image_uri', type=str)
    parser.add_argument('--secret_name', type=str)
    args, _ = parser.parse_known_args()

    print("Debug args:" + str(args))

    secret_name = args.secret_name
    secret = get_secret(secret_name)
    input_file = args.input_file
    repo_id = args.repo_id
    hf_local_repo = secret[args.hf_local_repo]
    hf_local_token = secret[args.hf_local_token]
    trained_revision = args.trained_revision
    author = args.author
    job_name = args.job_name
    dataset = args.dataset
    image_uri = args.image_uri
    repo_type = "model"

    dst = os.path.join(os.environ.get('SM_CHANNEL_TRAINING'), input_file)
    print("Debug: SM_CHANNEL_TRAIN" + dst)

    # Load npz file from local folder
    (x_train, y_train), (x_test, y_test) = load_data(dst)
    # normalize to 0-1
    x_train, x_test = x_train / 255.0, x_test / 255.0

    # Define the neural network architecture
    model = tf.keras.Sequential([
        tf.keras.layers.Flatten(input_shape=(28, 28)),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(10, activation='softmax')
    ])

    # Configures the model for training
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])

    # Train the model (a single epoch for demo purposes)
    model.fit(x_train, y_train, epochs=1)

    # Environment variable is from Sagemaker Training Toolkit (sagemaker-training)
    # Source: https://github.com/aws/sagemaker-training-toolkit/blob/master/ENVIRONMENT_VARIABLES.md#sm_input_dir
    # SM_INPUT_DIR=/opt/ml/input/
    # This will be the directory where the model will be stored when training is complete.
    model_save_dir = f"{os.environ.get('SM_INPUT_DIR')}/new"

    # Evaluate the model based on test data
    print("Evaluate on test data")
    results = model.evaluate(x_test, y_test)
    print("test loss, test acc:", results)

    # Saves a model as a TensorFlow SavedModel
    tf.keras.saving.save_model(model, model_save_dir)

    # Generate a model README file
    generate_readme(author, repo_id, trained_revision, job_name, dataset, image_uri, model_save_dir)

    # Upload the model t
    upload_model(model_save_dir, repo_id, repo_type, trained_revision, hf_local_repo, hf_local_token)
