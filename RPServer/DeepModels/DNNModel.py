from DeepModels.DNNSingelton import DNNSingelton
from os import listdir
import tensorflow as tf
import time
from keras_flops import get_flops

class DNNModel(DNNSingelton):
    dnn_models = {}

    def __init__(self):
        self.datasets = tf.keras.datasets
        self.layers = tf.keras.layers
        self.models = tf.keras.models

    def create_new_model(
            self,
            model_name,
            model_info,
            labels_num,
            layers_creator,
            input_shape=(5, 32, 1),
            optimizer='adam',
            metrics=None,
            building=""
    ):
        dense_layers_info = layers_creator("dense_layers", model_info)
        # model_name = ""
        model_name += "dense_"
        for layer in dense_layers_info:
            model_name += str(layer["units"]) + "_"
        model_name += building
        if metrics is None:
            metrics = [tf.keras.metrics.SparseCategoricalAccuracy()]
        model = self.models.Sequential()
        model.add(self.layers.Input(shape=input_shape))
        model.add(self.layers.Flatten())
        for dense_layer in dense_layers_info:
            units = dense_layer["units"]
            activation = dense_layer["activation_func"]
            model.add(self.layers.Dense(units, activation=activation))

        model.add(self.layers.Dropout(0.4))
        model.add(self.layers.Dense(units=labels_num, activation='softmax'))

        model.compile(optimizer=optimizer,
                      loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                      metrics=metrics)
        # model.save("models/dnn_models/" + name_of_model + ".h5")
        self.dnn_models[model_name] = model
        print(model.summary())
        flops = get_flops(model, batch_size=32)
        return model.count_params(), round(flops / 1000)

    def train(self, name_of_model, training_set, training_labels, validation_set, validation_labels, epochs, batch_size=32):
        start_time = time.time()
        history = self.dnn_models[name_of_model].fit(
            training_set,
            training_labels,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(validation_set, validation_labels)
        )
        self.dnn_models[name_of_model].save("models/dnn_models/" + name_of_model + ".h5")
        print(history)
        return history, self.dnn_models[name_of_model], int(time.time()-start_time)

    def predict(self, name_of_model, input_image):
        return self.dnn_models[name_of_model].predict(input_image)

    def evaluate(self, name_of_model, test_set, test_labels):
        print(test_set[0], test_labels)
        test_loss, test_acc = self.dnn_models[name_of_model].evaluate(
            test_set,
            test_labels,
            verbose=2
        )
        return test_loss, test_acc

    def load_models(self, path):
        for model_name in listdir(path):
            model = self.models.load_model(path+model_name)
            # print("dnn_" + model_name.split(".")[0])
            self.dnn_models["dnn_"+model_name.split(".")[0].replace("-", "_")] = model
        # print(self.dnn_models)


    def compress(self, path):
        for model_name in listdir(path):
            model = self.models.load_model(path+model_name)
            #Create a TFLite Converter Object from model we created
            converter = tf.lite.TFLiteConverter.from_keras_model(model=model)
            #Create a tflite model object from TFLite Converter
            tfmodel = converter.convert()
            # Save TFLite model into a .tflite file
            model_new_name = "dnn_"+model_name.split(".")[0].replace("-", "_")
            open("compressed_models/"+model_new_name+".tflite", "wb").write(tfmodel)