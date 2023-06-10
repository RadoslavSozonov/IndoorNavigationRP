import random
# from keras import datasets, layers, models
from firebaseConfig import Firebase
from DeepModels.CNNModel import CNNModel
import tensorflow as tf
import numpy as np
import time
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from DeepModels.DNNModel import DNNModel
from DeepModels.DTCModel import DTCModel
from DeepModels.KNNModel import KNNModel
from DeepModels.LinearClassificationModel import LinearClassificationModel
from DeepModels.RNNModel import RNNModel
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import pyRAPL
import psutil

from datetime import datetime

from DeepModels.SVMModel import SVMModel


class ModelCreator:

    def testModel(self, spectrogram, modelToTrain):
        if "cnn" in modelToTrain:
            return self.test(spectrogram, modelToTrain, CNNModel())

        if "dnn" in modelToTrain:
            return self.test(spectrogram, modelToTrain, DNNModel())

        if "rnn" in modelToTrain:
            return self.test(spectrogram, modelToTrain, RNNModel())

        if "linearSVM" in modelToTrain:
            return self.test(spectrogram, modelToTrain, LinearClassificationModel())

        if "knn" in modelToTrain:
            return self.test(spectrogram, modelToTrain, KNNModel())

        if "sgd" in modelToTrain:
            return self.test(spectrogram, modelToTrain, CNNModel())

    def test(self, spectrogram, modelToTrain, model):
        st = time.time()
        model.predict(modelToTrain, spectrogram)
        en = time.time()
        print(str(en-st))
        return en-st
    def trainModel(self, modelToTrain, building, model_name, model_info, model_epochs, model_batches):
        # print(modelName)
        data, labelsN = Firebase().getData(building)
        labels = [unit[0] for unit in data]
        map_label_encoding = {}
        value = 0
        for label in labels:
            if label not in map_label_encoding:
                map_label_encoding[label] = value
                value += 1
        spectrograms = [unit[1] for unit in data]
        encoded_labels = [map_label_encoding[label] for label in labels]
        shuffled_list = self.shuffle(spectrograms, encoded_labels)
        train_x = np.array([x[0] for x in shuffled_list])
        train_y = np.array([x[1] for x in shuffled_list])
        X_train, X_test, y_train, y_test = train_test_split(train_x, train_y, train_size=0.8, shuffle=True,
                                                            random_state=1)
        if modelToTrain == "cnn":
            self.create_and_train_cnn(model_name, model_info, labelsN, X_train, X_test, y_train, y_test, model_epochs,
                                      map_label_encoding.keys(), model_batches, building)
        if modelToTrain == "dnn":
            self.create_and_train_dnn(model_name, model_info, labelsN, X_train, X_test, y_train, y_test, model_epochs,
                                      map_label_encoding.keys(), model_batches, building)
        if modelToTrain == "rnn":
            self.create_and_train_rnn(model_name, model_info, labelsN, X_train, X_test, y_train, y_test, model_epochs,
                                      map_label_encoding.keys(), model_batches, building)
        if modelToTrain == "dbn":
            self.create_and_train_dbn(model_name, model_info, labelsN, X_train, X_test, y_train, y_test, model_epochs,
                                      map_label_encoding.keys(), model_batches)
        if modelToTrain == "linearSVM":
            self.create_and_train_ml_model("linearSVM", SVMModel(), model_info, X_train, X_test, y_train, y_test,
                                           building, map_label_encoding.keys())
        if modelToTrain == "dtc":
            self.create_and_train_ml_model("dtc", DTCModel(), model_info, X_train, X_test, y_train, y_test, building,
                                           map_label_encoding.keys())
        if modelToTrain == "knn":
            self.create_and_train_ml_model("knn", KNNModel(), model_info, X_train, X_test, y_train, y_test, building,
                                           map_label_encoding.keys())
        if modelToTrain == "sgd":
            self.create_and_train_ml_model("sgd", LinearClassificationModel(), model_info, X_train, X_test, y_train,
                                           y_test, building, map_label_encoding.keys())

    def create_and_train_ml_model(self, model_name, model, model_info, X_train, X_test, y_train, y_test, building,
                                  labels):
        date = datetime.now().strftime('%Y-%m-%d %H:%M').replace(" ", "_").replace(":", "_")
        model_name += date + "_" + building

        X_train = [np.array(array).flatten() for array in X_train]
        X_test = [np.array(array).flatten() for array in X_test]

        model_name = model.create_new_model(model_name, model_info)
        _, time = model.train(model_name, np.array(X_train), y_train)
        y_pred = model.predict(model_name, np.array(X_test))
        acc = model.evaluate(model_name, np.array(X_test), y_test)
        self.confusion_matrix_generator(model_name + "_" + str(round(acc, 3)), y_test, y_pred, labels, 0, time)

    def create_and_train_cnn(self, model_name, model_info, labelsN, X_train, X_test, y_train, y_test, model_epochs,
                             labels, model_batches, building):
        cnn_model = CNNModel()
        model_name = ""
        conv_pool_layers_info = self.layers_creator("conv_layers", model_info)
        dense_layers_info = self.layers_creator("dense_layers", model_info)

        model_name += "conv_"
        for layer in conv_pool_layers_info:
            model_name += str(layer["conv_filters"]) + "_"

        model_name += "dense_"
        for layer in dense_layers_info:
            model_name += str(layer["units"]) + "_"
        date = datetime.now().strftime('%Y-%m-%d %H:%M').replace(" ", "_").replace(":", "_")
        model_name += date + "_" + building

        start_energy = psutil.sensors_battery().percent

        params = cnn_model.create_new_model(model_name, conv_pool_layers_info, dense_layers_info, labels_num=labelsN,
                                            input_shape=(5, 32, 1))
        self.execute_model_train_and_prediction(cnn_model, model_name, X_train, y_train, X_test, y_test,
                                                epochs=model_epochs, labels=labels, model_batches=model_batches, params=params, energy=start_energy)

    def create_and_train_dnn(self, model_name, model_info, labelsN, X_train, X_test, y_train, y_test, model_epochs,
                             labels, model_batches, building):
        dnn_model = DNNModel()

        dense_layers_info = self.layers_creator("dense_layers", model_info)
        model_name = ""
        model_name += "dense_"
        for layer in dense_layers_info:
            model_name += str(layer["units"]) + "_"
        date = datetime.now().strftime('%Y-%m-%d %H:%M').replace(" ", "_").replace(":", "_")
        model_name += date + "_" + building
        start_energy = psutil.sensors_battery().percent
        params = dnn_model.create_new_model(model_name, dense_layers_info, labelsN)
        self.execute_model_train_and_prediction(dnn_model, model_name, X_train, y_train, X_test, y_test,
                                                epochs=model_epochs, labels=labels, model_batches=model_batches, params=params, start_energy=start_energy)

    def create_and_train_rnn(self, model_name, model_info, labelsN, X_train, X_test, y_train, y_test, model_epochs,
                             labels, model_batches, building):
        rnn_model = RNNModel()

        lstm_layers_info = model_info["lstm_units"]
        dense_layers_info = self.layers_creator("dense_layers", model_info)
        model_name = ""
        model_name += "lstm_"
        for layer in lstm_layers_info:
            model_name += str(layer) + "_"

        model_name += "dense_"
        for layer in dense_layers_info:
            model_name += str(layer["units"]) + "_"
        date = datetime.now().strftime('%Y-%m-%d %H:%M').replace(" ", "_").replace(":", "_")
        model_name += date + "_" + building
        start_energy = psutil.sensors_battery().percent

        params = rnn_model.create_new_model(model_name, dense_layers_info, units=lstm_layers_info, labels_num=labelsN,
                                            input_shape=(5, 32))
        self.execute_model_train_and_prediction(rnn_model, model_name, X_train, y_train, X_test, y_test,
                                                epochs=model_epochs, labels=labels, model_batches=model_batches, params=params, start_energy=start_energy)

    def layers_creator(self, name, model_info):
        layers_info = []
        layers = model_info[name]
        for layer in layers:
            layers_info.append(layer)
        return layers_info

    def execute_model_train_and_prediction(self, model, model_name, X_train, y_train, X_test, y_test, labels, params, epochs=20,
                                           model_batches=32, energy=100):
        history, _, time = model.train(
            model_name,
            X_train,
            y_train,
            X_test,
            y_test,
            epochs=epochs,
            batch_size=model_batches
        )
        # end_energy = psutil.sensors_battery().percent
        # end_power = psutil.sensors_powermonitor().power

        end_power = psutil.sensors_battery().percent
        battery = (energy - end_power)/100
        battery_current_capacity = 30310
        energy_consumed = round(battery*battery_current_capacity)
        # meter.end()
        results = model.predict(model_name, X_test)
        # print(results)
        # print(np.array(results).size)
        y_pred = [np.argmax(x) for x in results]
        acc = accuracy_score(y_test, y_pred)
        print(acc)
        self.confusion_matrix_generator(model_name + "_" + str(round(acc, 3)), y_test, y_pred, labels, params, time/60, history, epochs, energy=energy_consumed)

    def shuffle(self, spectrograms, encoded_labels):

        to_shuffle = []
        for i in range(len(encoded_labels)):
            to_shuffle.append((spectrograms[i], encoded_labels[i]))

        shuffled_list = []
        for i in range(10000):
            shuffled_list = random.sample(to_shuffle, k=len(to_shuffle))

        return shuffled_list

    def confusion_matrix_generator(self, name, y_act, y_pred, class_names, params, time, history, epochs, energy):
        cm = confusion_matrix(y_act, y_pred)
        fig = plt.figure(figsize=(16, 14))
        ax = plt.subplot()
        sns.heatmap(cm, annot=True, ax=ax, fmt='g');  # annot=True to annotate cells
        # labels, title and ticks
        ax.set_xlabel('Predicted', fontsize=20)
        ax.xaxis.set_label_position('bottom')
        plt.xticks(rotation=90)
        ax.xaxis.set_ticklabels(class_names, fontsize=10)
        ax.xaxis.tick_bottom()

        ax.set_ylabel('True', fontsize=20)
        ax.yaxis.set_ticklabels(class_names, fontsize=10)
        plt.yticks(rotation=0)
        name += "_" + str(params) + "_" + str(round(time, 2))
        plt.title(name, fontsize=20)
        # print(history.history)
        plt.savefig("confusion_matrices/" + name + "_" + energy + "mWH.png")
        plt.clf()
        train_loss = history.history['loss']
        val_loss = history.history['val_loss']
        train_acc = history.history['sparse_categorical_accuracy']
        val_acc = history.history['val_sparse_categorical_accuracy']
        xc = range(epochs)
        plt.clf()
        plt.plot(xc, train_loss, color="red", label="train_loss")
        plt.plot(xc, val_loss, color="blue", label="val_loss")
        plt.legend(loc="upper left")
        plt.savefig("plots/" + name + "_loss" + ".png")
        plt.clf()
        plt.plot(xc, train_acc, color="red", label="train_acc")
        plt.plot(xc, val_acc, color="blue", label="val_acc")
        plt.legend(loc="upper left")
        plt.savefig("plots/" + name + "_train" + ".png")
