import numpy as np

from DeepModels.DBNSingelton import DBNSingelton
from DeepBeliefNetwork.dbn.tensorflow import SupervisedDBNClassification
from sklearn.preprocessing import StandardScaler
from os import listdir
import tensorflow as tf


class DBNModel(DBNSingelton):
    def __init__(self):
        self.dbn_models = {}
        self.datasets = tf.keras.datasets
        self.layers = tf.keras.layers
        self.models = tf.keras.models

    def create_new_model(
            self,
            name_of_model,
            hidden_layers_structure=None,
            learning_rate_rbm=0.05,
            learning_rate=0.1,
            n_epochs_rbm=10,
            n_iter_backprop=100,
            batch_size=32,
            activation_function='relu',
            dropout_p=0.2
    ):
        if hidden_layers_structure is None:
            hidden_layers_structure = [256, 256]
        model = SupervisedDBNClassification(
            hidden_layers_structure=hidden_layers_structure,
            learning_rate_rbm=learning_rate_rbm,
            learning_rate=learning_rate,
            n_epochs_rbm=n_epochs_rbm,
            n_iter_backprop=n_iter_backprop,
            batch_size=batch_size,
            activation_function=activation_function,
            dropout_p=dropout_p
        )
        # model.save("models/dbn_models/" + name_of_model + ".pkl")
        self.dbn_models[name_of_model] = model

    def train(
            self,
            name_of_model,
            training_set,
            training_labels,
            normalize=False
    ):
        if normalize:
            ss = StandardScaler()
            training_set = ss.fit_transform(training_set)

        self.dbn_models[name_of_model].fit(np.array(training_set), np.array(training_labels))

    def predict(self, name_of_model, input_image):
        return self.dbn_models[name_of_model].predict(input_image)

    def evaluate(self, name_of_model, dense_layers_info):
        pass

    @staticmethod
    def load_models(self, path):
        for model_name in listdir(path):
            model = self.models.load_model(path + model_name)
            self.dbn_models[model.split(".")[0]] = model
