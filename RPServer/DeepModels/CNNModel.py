from DeepModels.CNNSingelton import CNNSingelton
from os import listdir
import tensorflow as tf
import numpy as np
import time
import tensorflow_model_optimization as tfmot

class CNNModel(CNNSingelton):
    cnn_models = {}
    def __init__(self):
        print("Fuckk")

        self.datasets = tf.keras.datasets
        self.layers = tf.keras.layers
        self.models = tf.keras.models

    def create_new_model(
            self,
            name_of_model,
            conv_pool_layers_info,
            dense_layers_info,
            input_shape=(5, 32, 1),
            optimizer='adam',
            metrics=None,
            labels_num=2
    ):

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

        self.cnn_models[name_of_model] = model
        print(model.summary())
        return model.count_params()

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
        # self.cnn_models[name_of_model].export(export_dir='compressed_models/')
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
            converter.target_spec.supported_ops = [
                tf.lite.OpsSet.TFLITE_BUILTINS,  # enable TensorFlow Lite ops.
                tf.lite.OpsSet.SELECT_TF_OPS  # enable TensorFlow ops.
            ]
            converter.experimental_enable_resource_variables = True
            #Create a tflite model object from TFLite Converter
            tfmodel = converter.convert()
            # Save TFLite model into a .tflite file
            model_new_name = "cnn_"+model_name.split(".")[0].replace("-", "_")
            open("compressed_models/"+model_new_name+".tflite", "wb").write(tfmodel)

    def quantization(self, model_name, trainX, trainY, testX, testY):
        quantize_model = tfmot.quantization.keras.quantize_model

        # q_aware stands for for quantization aware.
        q_aware_model = quantize_model(self.cnn_models[model_name])
        q_aware_model.compile(optimizer='adam',
                              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                              metrics=[tf.keras.metrics.SparseCategoricalAccuracy()])

        q_aware_model.fit(trainX, trainY,
                          batch_size=32, epochs=100, validation_data=(testX, testY))

        converter = tf.lite.TFLiteConverter.from_keras_model(q_aware_model)
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        quantized_tflite_model = converter.convert()

        interpreter = tf.lite.Interpreter(model_content=quantized_tflite_model)
        interpreter.allocate_tensors()

        input_index = interpreter.get_input_details()[0]["index"]
        output_index = interpreter.get_output_details()[0]["index"]  # Run predictions on every image in the "test" dataset.
        prediction_digits = []
        for i, test_image in enumerate(testX):
            # if i % 1000 == 0:
            #     print('Evaluated on {n} results so far.'.format(n=i))
            # Pre-processing: add batch dimension and convert to float32 to match with
            # the model's input data format.

            test_image = np.expand_dims(test_image.reshape((5, 32, 1)), axis=0).astype(np.float32)
            interpreter.set_tensor(input_index, test_image)  # Run inference.
            interpreter.invoke()  # Post-processing: remove batch dimension and find the digit with highest
            # probability.
            output = interpreter.tensor(output_index)
            digit = np.argmax(output()[0])
            prediction_digits.append(digit)

        # Compare prediction results with ground truth labels to calculate accuracy.
        prediction_digits = np.array(prediction_digits)
        accuracy = (prediction_digits == testY).mean()
        print(accuracy)
        open("compressed_models/" + model_name + ".tflite", "wb").write(quantized_tflite_model)

    def get_weights(self, model_name):
        print(self.cnn_models)
        print(self.cnn_models[model_name].get_weights())