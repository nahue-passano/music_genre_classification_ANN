# -*- coding: utf-8 -*-
"""
Created on Tue Nov 30 04:19:18 2021

@author: NPass
"""

import json
import numpy as np
from sklearn.model_selection import train_test_split
import tensorflow.keras as keras
import matplotlib.pyplot as plt

# Dataset load
def load_data(dataset_path):
    """
    Inputs:
        > dataset_path (str): Path of the database .json
    
    Outputs:
        > inputs (ndarray): Array with mfccs
        > targets (ndarray): Array with genre labels
    """
    
    with open(dataset_path, "r") as fp:
        data = json.load(fp)
    
    # Lists to arrays
    inputs = np.array(data["mfcc"])
    targets = np.array(data["labels"])
    
    return inputs, targets

def prepare_dataset(test_size, validation_size):
    """Loads data and splits it into train, validation and test sets.
    
    Inputs: 
        > test_size (float): Value in [0, 1] indicating percentage of data set to allocate to test split
        > validation_size (float): Value in [0, 1] indicating percentage of train set to allocate to validation split

    Outputs:
        > input_train (ndarray): Input training set
        > input_validation (ndarray): Input validation set
        > input_test (ndarray): Input test set
        > target_train (ndarray): Target training set
        > target_validation (ndarray): Target validation set
        > target_test (ndarray): Target test set
    """

    # Load data
    inputs, targets = load_data("data.json")

    # Split train/test
    input_train, input_test, target_train, target_test = train_test_split(inputs, targets, test_size=test_size)
    
    # Split train/validation
    input_train, input_validation, target_train, target_validation = train_test_split(input_train, target_train, test_size=validation_size)

    # Dimentionality adjustment for CNN
    
    input_train = input_train[..., np.newaxis]
    
    input_validation = input_validation[..., np.newaxis]
    
    input_test = input_test[..., np.newaxis]

    return input_train, input_validation, input_test, target_train, target_validation, target_test


def build_model(input_shape):
    
    # Model building (CNN with 5 hidden layers followed by a maxpooling layer)
    model = keras.Sequential()
    
    # 1st conv layer
    model.add(keras.layers.Conv2D(filters = 8 , kernel_size = (3,3) , activation = "relu" , input_shape = input_shape))
    model.add(keras.layers.MaxPool2D(pool_size = (2,2), strides = (1,1) , padding = "same"))
    model.add(keras.layers.BatchNormalization()) 
    
    
    # 2nd conv layer
    model.add(keras.layers.Conv2D(filters = 16 , kernel_size = (3,3) , activation = "relu" , input_shape = input_shape))
    model.add(keras.layers.MaxPool2D(pool_size = (2,2), strides = (1,1) , padding = "same"))
    model.add(keras.layers.BatchNormalization()) 
    
    # 3rd conv layer
    model.add(keras.layers.Conv2D(filters = 32 , kernel_size = (3,3) , activation = "relu" , input_shape = input_shape))
    model.add(keras.layers.MaxPool2D(pool_size = (2,2), strides = (1,1) , padding = "same"))
    model.add(keras.layers.BatchNormalization()) 
    
    # 4th conv layer
    model.add(keras.layers.Conv2D(filters = 64 , kernel_size = (3,3) , activation = "relu" , input_shape = input_shape))
    model.add(keras.layers.MaxPool2D(pool_size = (2,2), strides = (1,1) , padding = "same"))
    model.add(keras.layers.BatchNormalization()) 
    
    # 5ft conv layer
    model.add(keras.layers.Conv2D(filters = 128 , kernel_size = (3,3) , activation = "relu" , input_shape = input_shape))
    model.add(keras.layers.MaxPool2D(pool_size = (2,2), strides = (1,1) , padding = "same"))
    model.add(keras.layers.BatchNormalization()) 
    
    # Flatten and dense layer
    model.add(keras.layers.Flatten())       # Flatten
    model.add(keras.layers.Dense(units = 64 , activation = "relu")) # Dense
    model.add(keras.layers.Dropout(0.3))    # Dropout (for overfitting)
    
    # Output layer
    model.add(keras.layers.Dense(units=10 , activation = "softmax"))
    
    return model


def predict(model,input_i,target_i):
    
    input_i = input_i[np.newaxis, ...]
    prediction = model.predict(input_i)
    
    # Máxima probabilidad de la predicción
    predicted_index = np.argmax(prediction, axis = 1)
    print("Expected index: {}, Predicted index: {}".format(target_i,predicted_index))

if __name__ == "__main__":
    
    # Dataset process
    input_train, input_validation, input_test, target_train, target_validation, target_test = prepare_dataset(0.25,0.2)
    
    # CNN building
    input_shape = (input_train.shape[1],input_train.shape[2],input_train.shape[3])
    
    model = build_model(input_shape)
    
    # CNN compilation
    optimiser = keras.optimizers.Adam(learning_rate = 0.00005)
    model.compile(optimizer = optimiser,
                  loss = "sparse_categorical_crossentropy",
                  metrics = ['accuracy'])
    
    # CNN training
    model.fit(input_train,target_train, validation_data = (input_validation, target_validation), 
              batch_size = 32 , epochs = 70)
    
    # Test of the CNN
    test_error, test_accuracy = model.evaluate(input_test, target_test, verbose = 1)
    print("Accuracy on test set is: {}".format(test_accuracy))

    # Prediction with the CNN
    input_i = input_test[100]
    target_i = target_test[100]
    
    predict(model,input_i,target_i)