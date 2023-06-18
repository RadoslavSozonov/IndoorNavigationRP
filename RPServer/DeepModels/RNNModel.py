from DeepModels.RNNSingelton import RNNSingelton
from os import listdir
import tensorflow as tf
import time
import pickle

class RNNModel(RNNSingelton):
    rnn_models = {}

    def __init__(self):
        self.datasets = tf.keras.datasets
        self.layers = tf.keras.layers
        self.models = tf.keras.models

    def create_new_model(
            self,
            name_of_model,
            dense_layers_info,
            input_shape,
            optimizer="sgd",
            units=None,
            labels_num=2,
            metrics=None

    ):
        if units is None:
            units = [64]

        if metrics is None:
            metrics = [tf.keras.metrics.SparseCategoricalAccuracy()]
        model = self.models.Sequential()

        for i in range(len(units)):
            if i == 0:
                model.add(
                    self.layers.Bidirectional(
                        self.layers.LSTM(units[i], return_sequences=True),
                        input_shape=input_shape
                    )
                )
                print("0")
            else:
                model.add(
                    self.layers.Bidirectional(
                        self.layers.LSTM(units[i], return_sequences=True)
                    )
                )
                print("1")

        model.add(self.layers.BatchNormalization())
        model.add(self.layers.Flatten())
        for dense_layer in dense_layers_info:
            units = dense_layer["units"]
            activation = dense_layer["activation_func"]
            model.add(self.layers.Dense(units, activation=activation, ))

        model.add(self.layers.Dropout(0.4))
        model.add(self.layers.Dense(labels_num))

        model.compile(
            loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
            optimizer=optimizer,
            metrics=metrics,
        )
        # model.save("models/rnn_models/" + name_of_model + ".h5")
        self.rnn_models[name_of_model] = model
        print(model.summary())
        return model.count_params()

    def train(self, name_of_model, training_set, training_labels, validation_set, validation_labels, epochs, batch_size=64):
        start_time = time.time()
        history = self.rnn_models[name_of_model].fit(
            training_set,
            training_labels,
            validation_data=(validation_set, validation_labels),
            batch_size=batch_size,
            epochs=epochs
        )
        print(history)
        self.rnn_models[name_of_model].save("models/rnn_models/" + name_of_model + ".h5")
        return history, self.rnn_models[name_of_model], int(time.time()-start_time)

    def predict(self, name_of_model, input_image):
        return self.rnn_models[name_of_model].predict(input_image)

    def evaluate(self, name_of_model, test_set, test_labels):
        test_loss, test_acc = self.rnn_models[name_of_model]\
            .evaluate(
            test_set,
            test_labels,
            verbose=2
        )
        return test_loss, test_acc

    def load_models(self, path):
        for model_name in listdir(path):
            model = pickle.load(open(path + model_name, 'rb'))
            # print("rnn_" + model_name.split(".")[0])
            self.rnn_models["rnn_"+model_name.split(".")[0].replace("-", "_")] = model
        # print(self.rnn_models)

    def compress(self, path):
        for model_name in listdir(path):
            model = self.models.load_model(path+model_name)
            #Create a TFLite Converter Object from model we created
            converter = tf.lite.TFLiteConverter.from_keras_model(model=model)
            #Create a tflite model object from TFLite Converter
            tfmodel = converter.convert()
            # Save TFLite model into a .tflite file
            model_new_name = "rnn_"+model_name.split(".")[0].replace("-", "_")
            open("compressed_models/"+model_new_name+".tflite", "wb").write(tfmodel)




