from Converter import Converter
from DataLoader import DataLoader
from DeepModels.CNNModel import CNNModel
import numpy as np
import time
from sklearn.metrics import accuracy_score
from DeepModels.DNNModel import DNNModel
from DeepModels.RNNModel import RNNModel
import psutil
from datetime import datetime
from PlotService import PlotService
from SpectogramCreator import SpectogramCreator


class ModelCreator:

    def __init__(self):
        self.interval_rate = 4410
        self.chirp_error_amount = 2
        self.models = {
            "cnn": {"model": CNNModel, "shape": (5, 32, 1)},
            "dnn": {"model": DNNModel, "shape": (5, 32, 1)},
            "rnn": {"model": RNNModel, "shape": (5, 32, 1)}
        }

    def trainModel(self, modelToTrain, building, model_info, model_epochs, model_batches):
        data_info = DataLoader().load_model_data_from_db(building=building, train_size=0.8)
        self.process_model(
            self.models[modelToTrain]["model"],
            modelToTrain,
            model_info,
            data_info,
            input_shape=self.models[modelToTrain]["shape"],
            model_epochs=model_epochs,
            model_batches=model_batches,
            building=building
        )

    def process_model(self, model, name_of_model, model_info, data_info, input_shape, model_epochs,
                             model_batches, building):

        params, flops, model_name = model.create_new_model(
            model_name=name_of_model,
            model_info=model_info,
            labels_num=data_info["labelsN"],
            input_shape=input_shape,
            building=building,
            layers_creator=self.layers_creator
        )
        start_energy = psutil.sensors_battery().percent
        history, _, time = model.train(
            model_name,
            data_info["X_train"],
            data_info["y_train"],
            data_info["X_test"],
            data_info["y_test"],
            epochs=model_epochs,
            batch_size=model_batches
        )

        end_power = psutil.sensors_battery().percent
        battery = (start_energy - end_power) / 100
        battery_current_capacity = 30310
        energy_consumed = round(battery * battery_current_capacity)
        results = model.predict(model_name, data_info["X_test"],)

        y_pred = [np.argmax(x) for x in results]
        acc = accuracy_score(data_info["y_test"], y_pred)

        print(acc)
        date = datetime.now().strftime('%Y-%m-%d %H:%M').replace(" ", "_").replace(":", "_")
        data_model_results = {
            "date": date,
            "acc": str(round(acc, 3)),
            "params": str(params),
            "time": str(round(time / 60, 2)),
            "flops": str(flops) + "K",
            "energy": str(energy_consumed) + "mWh"
        }
        model_name = model_name + "_" + date
        self.confusion_matrix_generator(model_name, data_info["y_test"], y_pred, data_info["labels"])
        self.plot_generator(model_name, history, model_epochs)
        self.write_to_file(model_name, data_model_results)

    def layers_creator(self, name, model_info):
        layers_info = []
        layers = model_info[name]
        for layer in layers:
            layers_info.append(layer)
        return layers_info

    def confusion_matrix_generator(self, name, y_act, y_pred, class_names):
        PlotService().confusion_matrix_creator(name, y_act, y_pred, class_names)

    def plot_generator(self, name, history, epochs):
        train_loss = history.history['loss']
        val_loss = history.history['val_loss']
        train_acc = history.history['sparse_categorical_accuracy']
        val_acc = history.history['val_sparse_categorical_accuracy']
        xc = range(epochs)
        data = [
            {
                "x": xc,
                "y": train_loss,
                "color": "red",
                "label": "train_loss"
            }, {
                "x": xc,
                "y": val_loss,
                "color": "blue",
                "label": "val_loss"
            }
        ]
        name = name + "_loss"
        PlotService().line_plot_creator(name, data)

        data = [
            {
                "x": xc,
                "y": train_acc,
                "color": "red",
                "label": "train_acc"
            }, {
                "x": xc,
                "y": val_acc,
                "color": "blue",
                "label": "val_acc"
            }
        ]
        name = name + "_train"
        PlotService().line_plot_creator(name, data)

    def write_to_file(self, model_name, data_results):
        name = 'text_files_models_results/' + model_name + ".txt"
        mode = 'a'
        data = ""
        for key in data_results.keys():
            data += f"{key}: {data_results[key]}\n"
        Converter.to_txt_file(name, mode, data)

    def evaluate(self, model_name, data_set):
        models = {}
        buildings_name = ["EWI15_6", "EWI16_6"]
        if model_name == "all":
            models.update(CNNModel().cnn_models)
            models.update(RNNModel().rnn_models)
            models.update(DNNModel().dnn_models)

        if data_set == "all":

            for building_name in buildings_name:
                name = 'text_files/' + building_name + "_results.txt"
                mode = "a"
                data = ""

                X_train, X_test, y_train, y_test, labelsN, map_label_encoding = DataLoader().load_model_data_from_db(
                    building=building_name, train_size=1)

                for model_name in models:
                    print(model_name)
                    loss, accuracy = models[model_name].evaluate(X_train, y_train, verbose=2)
                    data += f"{model_name}: {accuracy}, {loss}\n"

                data += f"\n"
                Converter().to_txt_file(name, mode, data)

    def predict_location(self, model_name, dictionary):
        spectrogramCreator = SpectogramCreator()
        np_arr = Converter().json_to_audio_data_converter(dictionary)
        chirp_sample_offset = 0

        for i in range(1):
            start_rate = int(i * self.interval_rate + chirp_sample_offset)
            sliced = np_arr[start_rate:(int(start_rate + self.interval_rate))]
            spectrogram = spectrogramCreator.createSpectrogramScipy(sliced)
            spectrogram = spectrogram.reshape((1, 5, 32, 1))
            return str(self.testModel(spectrogram, model_name))

    def testModel(self, spectrogram, modelToTrain):
        st = time.time()
        self.models[modelToTrain[:3]].predict(modelToTrain, spectrogram)
        en = time.time()
        return en - st
