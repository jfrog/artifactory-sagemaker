from sagemaker_inference import model_server


model_server.start_model_server(handler_service="/home/model-server/inference.py:handle")