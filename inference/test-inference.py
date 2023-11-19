from sagemaker.predictor import Predictor
import numpy as np
import matplotlib.pyplot as plt
from keras.datasets import mnist
from sagemaker.serializers import JSONSerializer
import sagemaker

#Sagemaker inference endpoint name
endpoint = 'tensorflow-v1'

sm_session = sagemaker.Session()

#Retrieve an example test dataset to test

# Load the MNIST dataset and split it into training and testing sets
(x_train, y_train), (x_test, y_test) = mnist.load_data('../mnist.npz')
# Select a random example from the training set
example_index = np.random.randint(0, x_train.shape[0])
example_image = x_train[example_index]
example_label = y_train[example_index]

# Print the label and show the image
print(f"Label: {example_label}")
plt.imshow(example_image, cmap='gray')
plt.show()


#Prepare the input data for the model inference
data = {"instances": example_image.tolist()}

#Initiliaze real-time predictions against SageMaker endpoint
predictor = Predictor(endpoint_name=endpoint, sagemaker_session=sm_session)
#Declare the model input data serelization to Json
predictor.serializer = JSONSerializer() #update the predictor to use the JSONSerializer

#make the prediction
r = predictor.predict(data)
print("Prediction: {}".format(r))
