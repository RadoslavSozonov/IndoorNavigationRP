from DeepModels.DNNSingelton import DNNSingelton
import tensorflow as tf


class DNNModel(DNNSingelton):

    def __init__(self):
        self.dnn_models = {}
        self.datasets = tf.keras.datasets
        self.layers = tf.keras.layers
        self.models = tf.keras.models

    def create_new_model(
            self,
            name_of_model,
            dense_layers_info,
            input_shape=(5, 32, 1),
            optimizer='adam',
            metrics=None
    ):

        model = self.models.Sequential()

        for dense_layer in dense_layers_info:
            units = dense_layer["units"]
            activation = dense_layer["activation_func"]
            model.add(self.layers.Dense(units, activation=activation))

        # model.add(self.layers.Dense(units, activation=activation))

        model.compile(optimizer=optimizer,
                      loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                      metrics=metrics)
        self.dnn_models[name_of_model] = model

    def train(self, name_of_model, training_set, training_labels, validation_set, validation_labels, epochs):
        history = self.dnn_models[name_of_model].fit(
            training_set,
            training_labels,
            epochs=epochs,
            validation_data=(validation_set, validation_labels)
        )
        return history, self.dnn_models[name_of_model]

    def predict(self, name_of_model, input):
        return self.dnn_models[name_of_model].predict(input)

    def evaluate(self, name_of_model, test_set, test_labels):
        test_loss, test_acc = self.dnn_models[name_of_model]\
            .evaluate(
            test_set,
            test_labels,
            verbose=2
        )
        return test_loss, test_acc