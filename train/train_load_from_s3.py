import tensorflow as tf
import numpy as np
import argparse
import os

#Load npz file from loacl folder
def load_data(path):
    with np.load(path) as f:
        x_train, y_train = f['x_train'], f['y_train']
        x_test, y_test = f['x_test'], f['y_test']
        return (x_train, y_train), (x_test, y_test)

#main
if __name__ =='__main__':
    
    #Parse train job input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--training', type=str,default=os.environ.get('SM_CHANNEL_TRAINING'))
    parser.add_argument('--input_file', type=str)
    args, _ = parser.parse_known_args()
    
    print("Debug args:"+str(args))
    
    input_file = args.input_file
    dst = os.path.join(os.environ.get('SM_CHANNEL_TRAINING'),input_file)
    print("Debug: SM_CHANNEL_TRAIN"+dst)
    
    #Load npz file from loacl folder
    (x_train, y_train), (x_test, y_test) = load_data(dst)
    #normalize to 0-1
    x_train, x_test = x_train / 255.0, x_test / 255.0 #normalize to 0-1
    
    #Define the neural network architecture
    model = tf.keras.models.Sequential([
        tf.keras.layers.Flatten(input_shape=(28, 28)),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(10, activation='softmax')
    ])
    
    #Configures the model for training
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
    
    #Trains the model
    model.fit(x_train, y_train, epochs=1)
    
    model_save_dir = f"{os.environ.get('SM_MODEL_DIR')}/"
    # Evaluate the model based on test data
    print("Evaluate on test data")
    results = model.evaluate(x_test, y_test)
    print("test loss, test acc:", results)
    # Saves a model as a TensorFlow SavedModel
    tf.saved_model.save(model, model_save_dir)
