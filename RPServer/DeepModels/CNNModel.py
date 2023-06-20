from DeepModels.CNNSingelton import CNNSingelton
from os import listdir
import tensorflow as tf
import time
from keras_flops import get_flops

class CNNModel(CNNSingelton):
    cnn_models = {}
    def __init__(self):
        self.datasets = tf.keras.datasets
        self.layers = tf.keras.layers
        self.models = tf.keras.models

    def create_new_model(
            self,
            model_name,
            model_info,
            layers_creator,
            input_shape=(5, 32, 1),
            optimizer='adam',
            metrics=None,
            labels_num=2,
            building=""
    ):

        # model_name = ""
        conv_pool_layers_info = layers_creator("conv_layers", model_info)
        dense_layers_info = layers_creator("dense_layers", model_info)

        model_name += "conv_"
        for layer in conv_pool_layers_info:
            model_name += str(layer["conv_filters"]) + "_"

        model_name += "dense_"
        for layer in dense_layers_info:
            model_name += str(layer["units"]) + "_"

        model_name += building

        if metrics is None:
            metrics = [tf.keras.metrics.SparseCategoricalAccuracy()]
        model = self.models.Sequential()

        print(model)
        for conv_pool_layer in conv_pool_layers_info:
            conv_filters = conv_pool_layer["conv_filters"]
            conv_activation_func = conv_pool_layer["conv_activation_func"]
            conv_layer_filter_size = conv_pool_layer["conv_layer_filter_size"]

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

            else:
                model.add(
                    self.layers.Conv2D(
                        conv_filters,
                        (conv_layer_filter_size, conv_layer_filter_size),
                        activation=conv_activation_func,
                        strides=(1, 1),
                        padding="same"
                    )
                )
            if "pool_layer_filter_size" in conv_pool_layer:
                pool_layer_filter_size = conv_pool_layer["pool_layer_filter_size"]
                model.add(self.layers.MaxPooling2D(
                    (
                        pool_layer_filter_size,
                        pool_layer_filter_size
                    ),
                    strides=(2, 2),
                    padding="valid"
                ))

        model.add(self.layers.Flatten())

        for dense_layer in dense_layers_info:
            units = dense_layer["units"]
            activation = dense_layer["activation_func"]
            model.add(self.layers.Dense(units, activation=activation))
        model.add(self.layers.Dropout(0.4))
        model.add(self.layers.Dense(units=labels_num))

        model.compile(optimizer=optimizer,
                      loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                      metrics=metrics)

        self.cnn_models[model_name] = model
        print(model.summary())
        flops = get_flops(model, batch_size=32)
        return model.count_params(), round(flops/1000), model_name

    def train(self, name_of_model, training_set, training_labels, validation_set, validation_labels, epochs=20, batch_size=32):
        # print(training_set)
        # print(training_labels)
        start_time = time.time()
        history = self.cnn_models[name_of_model].fit(
            training_set,
            training_labels,
            batch_size=batch_size,
            epochs=epochs,
            validation_data=(validation_set, validation_labels),
            shuffle=False
        )
        self.cnn_models[name_of_model].save("models/cnn_models/" + name_of_model + ".h5")
        print(history)
        return history, self.cnn_models[name_of_model], int(time.time()-start_time)

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

    def load_models(self, path):
        for model_name in listdir(path):
            model = self.models.load_model(path+model_name)
            # print("cnn_"+model_name.split(".")[0])
            self.cnn_models["cnn_"+model_name.split(".")[0].replace("-", "_")] = model

    def compress(self, path):
        for model_name in listdir(path):
            model = self.models.load_model(path+model_name)
            #Create a TFLite Converter Object from model we created
            converter = tf.lite.TFLiteConverter.from_keras_model(model=model)
            #Create a tflite model object from TFLite Converter
            tfmodel = converter.convert()
            # Save TFLite model into a .tflite file
            model_new_name = "cnn_"+model_name.split(".")[0].replace("-", "_")
            open("compressed_models/"+model_new_name+".tflite", "wb").write(tfmodel)