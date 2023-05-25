from DeepModels.RNNSingelton import RNNSingelton
import tensorflow as tf

class RNNModel(RNNSingelton):
    def __init__(self):
        self.cnn_models = {}
        self.datasets = tf.keras.datasets
        self.layers = tf.keras.layers
        self.models = tf.keras.models

    def create_new_model(
            self,
            name_of_model,
            dense_layers_info
    ):
        pass

    def train(self, name_of_model, dense_layers_info):
        pass

    def predict(self, name_of_model, dense_layers_info):
        pass

    def evaluate(self, name_of_model, dense_layers_info):
        pass
