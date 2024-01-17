# This is the script that will be used in the inference container
import tensorflow as tf
import numpy as np
import os
from huggingface_hub import snapshot_download
from sagemaker_inference import content_types, decoder, encoder
from sagemaker_inference.default_handler_service import DefaultHandlerService
import logging
import boto3
from botocore.exceptions import ClientError
import json

logger = logging.getLogger("sagemaker-inference")
logger.setLevel(logging.DEBUG)

class HandlerService(DefaultHandlerService):
    """Handler service that is executed by the model server.
    Determines specific default inference handlers to use based on model being used.
    This class extends ``DefaultHandlerService``, which define the following:
        - The ``handle`` method is invoked for all incoming inference requests to the model server.
        - The ``initialize`` method is invoked at model server start up.
    Based on: https://github.com/awslabs/mxnet-model-server/blob/master/docs/custom_service.md
    """
    def __init__(self):
        self.error = None
        self._context = None
        self._batch_size = 0
        self.initialized = False
        self.model = None
    
    def initialize(self, context):
        """
        Initialize model. This will be called during model loading time
        :param context: Initial context contains model server system properties.
        """
        logger.debug("DEBUG initialize() start. model_dir: {}".format(os.environ.get('JF_MODEL_DIR')))
        self._context = context
        self.initialized = True
        model_dir = os.environ.get('JF_MODEL_DIR')
        self.model_fn(model_dir)
        logger.debug("DEBUG initialize() finish.")

    def handle(self, data, context):
        """
        Call preprocess, inference and post-process functions
        :param data: input data
        :param context: mms context
        """
        logger.debug("DEBUG self.handle() start.")
        model_input = self.input_fn(data, context)
        model_out = self.predict_fn(model_input, self.model)
        logger.debug("DEBUG self.handle() model_out: {} type: {}.".format(model_out, type(model_out)))
        #output_text = json.dumps({"output_text": model_out.tolist()})
        #logger.debug("DEBUG self.handle() return: {} type: {}.".format(output_text,type(list(output_text))))
        output_text = model_out.tolist()
        logger.debug("DEBUG self.handle() output_text: {} type: {} len: {}.".format(output_text, type(output_text), len(output_text)))
        return output_text

    def get_secret(self, secret_name):
        """
        Get JFrog huggingface credentials and endpoint from an AWS secret
        """
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

    def model_fn(self, model_dir):
        """
        Load the model and tokenizer for inference
        """
        
        secret = self.get_secret(os.environ.get('JF_SECRET_NAME'))

        # Declare the Huggingface client environment variables
        os.environ['HF_ENDPOINT'] = secret[os.environ.get('JF_SECRET_HF_LOCAL_REPO')]
        os.environ['HUGGING_FACE_HUB_TOKEN'] = secret[os.environ.get('JF_SECRET_HF_LOCAL_TOKEN')]

        #logger.debug("DEBUG model_fn() os.environ['HF_ENDPOINT']: {} os.environ['HUGGING_FACE_HUB_TOKEN']: {}".format(os.environ['HF_ENDPOINT'],
        #                                                                                                              os.environ['HUGGING_FACE_HUB_TOKEN']))

        # Download the model from Artifactory
        snapshot_download(token=os.environ['HUGGING_FACE_HUB_TOKEN'],
                          endpoint=os.environ['HF_ENDPOINT'],
                          repo_id=os.environ.get('JF_REPO_ID'),
                          local_dir=model_dir,
                          revision=os.environ.get('JF_REVISION'))

        # Load the model
        self.model = tf.keras.saving.load_model(model_dir)
        logger.debug("DEBUG model_fn() finish.")
        return self.model

    def predict_fn(self, input_data, model_dict):
        """
        Make a prediction with the model
        """
        logger.debug("DEBUG predict_fn() start.")
        logger.debug("DEBUG predict_fn() input_data: {}.".format(input_data))
        logger.debug("DEBUG predict_fn() converted input_data: {}.".format(json.loads(input_data[0]["body"].decode('utf-8'))['instances']))

        np_array_input_data = json.loads(input_data[0]["body"].decode('utf-8'))['instances']
        data = np.expand_dims(np_array_input_data, axis=0)
        r = model_dict.predict(data)

        # Round the prediction results
        model_output = np.round(r, 1)
        logger.debug("Prediction: {}".format(np.round(r, 1)))
        logger.debug("DEBUG predict_fn() finish.")
        return model_output

    def input_fn(self, request_body, context):
        """
        Transform the input request to a dictionary
        """
        logger.debug("DEBUG input_fn() start.")
        logger.debug("DEBUG input_fn() input: {}.".format(np.array(request_body)))
        return np.array(request_body)

    def output_fn(self, prediction, accept):
        """A default output_fn for PyTorch. Serializes predictions from predict_fn to
        JSON, CSV or NPY format.

        Args:
            prediction: a prediction result from predict_fn
            accept: type which the output data needs to be serialized

        Returns: output data serialized
        """
        logger.debug("DEBUG output_fn() start.")
        return encoder.encode(prediction, accept)

_service = HandlerService()

def handle(data, context):
    logger.debug("DEBUG handle() start.")
    if not _service.initialized:
        _service.initialize(context)
    
    if data is None:
        return None

    logger.debug("DEBUG handle() finish.")
    return _service.handle(data, context)
