from DeepModels.CNNSingelton import CNNSingelton
import tensorflow as tf


class CNNModel(CNNSingelton):

    def __init__(self):
        self.cnn_models = {}
        self.datasets = tf.keras.datasets
        self.layers = tf.keras.layers
        self.models = tf.keras.models

    '''
        input_shape=(5, 32, 1),
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
        optimizer = 'adam'
        metrics = ['accuracy']
    '''
    def create_new_model(
            self,
            name_of_model,
            conv_pool_layers_info,
            dense_layers_info,
            input_shape=(5, 32, 1),
            optimizer='adam',
            metrics=None
    ):

        if metrics is None:
            metrics = ['accuracy']
        model = self.models.Sequential()

        for conv_pool_layer in conv_pool_layers_info:
            conv_filters = conv_pool_layer["conv_filters"]
            conv_activation_func = conv_pool_layer["conv_activation_func"]
            conv_layer_filter_size = conv_pool_layer["conv_layer_filter_size"]
            pool_layer_filter_size = conv_pool_layer["pool_layer_filter_size"]
            if conv_pool_layer["layer_num"] == 1:
                model.add(
                    self.layers.Conv2D(
                        conv_filters,
                        (conv_layer_filter_size, conv_layer_filter_size),
                        activation=conv_activation_func,
                        input_shape=input_shape,
                        strides=(1, 1),
                        padding="same"
                    )
                )
                model.add(self.layers.MaxPooling2D(
                    (
                        pool_layer_filter_size,
                        pool_layer_filter_size,
                    ),
                    strides=(2, 2),
                    padding="valid"
                ))
                continue

            model.add(
                self.layers.Conv2D(
                    conv_filters,
                    (conv_layer_filter_size, conv_layer_filter_size),
                    activation=conv_activation_func
                )
            )
            model.add(self.layers.MaxPooling2D(
                (
                    pool_layer_filter_size,
                    pool_layer_filter_size
                )
            ))

        model.add(self.layers.Flatten())

        for dense_layer in dense_layers_info:
            units = dense_layer["units"]
            activation = dense_layer["activation_func"]
            model.add(self.layers.Dense(units, activation=activation, ))
        # model.add(self.layers.Dense(10))

        model.compile(optimizer=optimizer,
                      loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                      metrics=metrics)
        self.cnn_models[name_of_model] = model

    def train(self, name_of_model, training_set, training_labels, epochs, validation_set=None, validation_labels=None):
        print(self.cnn_models[name_of_model])
        history = self.cnn_models[name_of_model].fit(
            training_set,
            training_labels,
            epochs=epochs,
            validation_data=(training_set, training_labels)
        )
        return history, self.cnn_models[name_of_model]

    def predict(self, name_of_model, input_image):
        return self.cnn_models[name_of_model].predict(input_image)

    def evaluate(self, name_of_model, test_set, test_labels):
        test_loss, test_acc = self.cnn_models[name_of_model]\
            .evaluate(
            test_set,
            test_labels,
            verbose=2
        )
        return test_loss, test_acc