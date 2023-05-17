import firebaseConfig as firebase
from DeepModels.CNNModel import CNNModel
import tensorflow as tf
import numpy as np

class ModelCreator:
    '''

    conv_pool_layers_info
        [
            {
                "conv_filters":,
                "conv_activation_func":,
                "conv_layer_filter_size":,
                "pool_layer_filter_size":,
                "layer_num":
            }
        ]
        dense_layers_info
        [
            {
                "units":,
                "activation_func":
            }
        ]

    '''
    def trainModel(self, modelName, building):
        # print(modelName)
        data, labelsN = firebase.get_from_real_time_database(building)
        if modelName == "cnn":
            cnn_model = CNNModel()

            #These lists will store information about the convolutional and dense layers of the CNN model, respectively.
            conv_pool_layers_info = []
            dense_layers_info = []

            # is a list that contains the labels associated with the data.
            labels = [unit[0] for unit in data]
            map_label_encoding = {}
            value = 0
            for label in labels:
                if label not in map_label_encoding:
                    map_label_encoding[label] = value
                    value += 1
            spectrograms = [unit[1] for unit in data]
            conv_pool_layers_info.append({
                "conv_filters": 16,
                "conv_activation_func": 'relu',
                "conv_layer_filter_size": 4,
                "pool_layer_filter_size": 2,
                "layer_num": 1
            })
            conv_pool_layers_info.append({
                "conv_filters": 32,
                "conv_activation_func": 'relu',
                "conv_layer_filter_size": 4,
                "pool_layer_filter_size": 2,
                "layer_num": 1
            })
            dense_layers_info.append({
                "units": 1024,
                "activation_func": 'relu'
            })
            dense_layers_info.append({
                "units": labelsN,
                "activation_func": 'relu'
            })
            cnn_model.create_new_model("my_first_model", conv_pool_layers_info, dense_layers_info)

            encoded_labels = [map_label_encoding[label] for label in labels]
            cnn_model.train("my_first_model", tf.stack(spectrograms), tf.stack(encoded_labels), 20)
            return cnn_model
        if modelName == "dnn":
            return CNNModel()

