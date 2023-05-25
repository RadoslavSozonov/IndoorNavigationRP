import random
from keras import datasets, layers, models
import firebaseConfig as firebase
from DeepModels.CNNModel import CNNModel
import tensorflow as tf
import numpy as np

from DeepModels.DNNModel import DNNModel


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
    def trainModel(self, modelToTrain, building, model_name, model_info):
        # print(modelName)
        data, labelsN = firebase.get_from_real_time_database(building)
        labels = [unit[0] for unit in data]
        map_label_encoding = {}
        value = 0
        for label in labels:
            if label not in map_label_encoding:
                map_label_encoding[label] = value
                value += 1
        spectrograms = [unit[1] for unit in data]
        encoded_labels = [map_label_encoding[label] for label in labels]

        if modelToTrain == "cnn":
            self.create_and_train_cnn(model_name, model_info, labelsN, spectrograms, encoded_labels)
        if modelToTrain == "dnn":
            self.create_and_train_dnn(model_name, model_info, labelsN, spectrograms, encoded_labels)

    def create_and_train_cnn(self, model_name, model_info, labelsN, spectrograms, encoded_labels):
        cnn_model = CNNModel()
        conv_pool_layers_info = []
        dense_layers_info = []

        conv_layers = model_info["conv_layers"]
        for layer in conv_layers:
            conv_pool_layers_info.append(layer)

        dense_layers = model_info["dense_layers"]
        for layer in dense_layers:
            dense_layers_info.append(layer)

        dense_layers_info.append({
            "units": labelsN,
            "activation_func": 'relu'
        })
        to_shuffle = []
        for i in range(len(encoded_labels)):
            to_shuffle.append((spectrograms[i], encoded_labels[i]))

        shuffled_list = []
        for i in range(10000):
            shuffled_list = random.sample(to_shuffle, k=len(to_shuffle))
        print(labelsN)

        # self.tensorflow_dummy_example(
        #     [x[0] for x in shuffled_list],
        #     [x[0] for x in shuffled_list],
        #     [x[1] for x in shuffled_list],
        #     [x[1] for x in shuffled_list]
        # )

        cnn_model.create_new_model(model_name, conv_pool_layers_info, dense_layers_info, labels_num=labelsN, input_shape=(5, 32, 1))
        cnn_model.train(
            model_name,
            [x[0] for x in shuffled_list][:300],
            [x[1] for x in shuffled_list][:300],
            20,
            [x[0] for x in shuffled_list][300:],
            [x[1] for x in shuffled_list][300:]
        )

    def tensorflow_dummy_example(self, train_images, test_images, train_labels, test_labels):
        # (train_images, train_labels), (test_images, test_labels) = datasets.cifar10.load_data()
        # train_images, test_images = train_images / 255.0, test_images / 255.0
        model = models.Sequential()
        model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=(5, 32, 1)))
        model.add(layers.MaxPooling2D((2, 2)))
        model.add(layers.Conv2D(64, (3, 3), activation='relu'))
        model.add(layers.MaxPooling2D((2, 2)))
        model.add(layers.Conv2D(64, (3, 3), activation='relu'))
        model.summary()
        model.add(layers.Flatten())
        model.add(layers.Dense(64, activation='relu'))
        model.add(layers.Dense(10))
        model.compile(optimizer='adam',
                      loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                      metrics=['accuracy'])

        history = model.fit(train_images, train_labels, epochs=10,
                            validation_data=(test_images, test_labels))

    def create_and_train_dnn(self, model_name, model_info, labelsN, spectrograms, encoded_labels):
        dnn_model = DNNModel()
        dense_layers_info = []

        dense_layers = model_info["dense_layers"]
        for layer in dense_layers:
            dense_layers_info.append(layer)

        dense_layers_info.append({
            "units": labelsN,
            "activation_func": 'relu'
        })

        dnn_model.create_new_model(model_name, dense_layers)
        dnn_model.train(model_name, tf.stack(spectrograms), tf.stack(encoded_labels), 20)

