from os import listdir

from flask import Flask, request
import json
import numpy as np
from scipy.io import wavfile
from matplotlib import pyplot as plt
from scipy.signal import spectrogram
from scipy.signal.windows import hann
from scipy.io.wavfile import write
from DeepModels.CNNModel import CNNModel
from DeepModels.DNNModel import DNNModel
from DeepModels.KNNModel import KNNModel
from DeepModels.LinearClassificationModel import LinearClassificationModel
from DeepModels.RNNModel import RNNModel
from ModelCreator import ModelCreator
from SpectogramCreator import SpectogramCreator
import os
from datetime import datetime

app = Flask(__name__)

interval = 0.1
sample_rate = 44100
chirp_amount = 204
# amount of chirps that are ignored, since some of the last chirps dont work
chirp_error_amount = 2
# chirp_sample_offset = 0

interval_rate = sample_rate * interval


def create_spectrogram(array, filename):
    print(array.shape)
    f, t, Sxx = spectrogram(array, 44100, window=hann(256, sym=False))
    plt.pcolormesh(t, f, Sxx, shading='gouraud')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.savefig(filename)


@app.route('/convert_wav_to_text_file')
def convert_wav_to_text_file():
    for place in os.listdir("wav_files/"):
        if not place.__contains__("EWI"):
            continue
        samplerate, wav_array = wavfile.read('wav_files/'+place)
        with open('text_files/'+place.split(".")[0]+".txt", 'w') as f:
            for line in wav_array:
                f.write(f"{line}\n")
        # np_arr = np.array(wav_array)
        # np.savetxt('text_files/'+place.split(".")[0]+".txt", np_arr, delimiter=',')
    return "Done"

@app.route('/add_room', methods=['POST'])
def add_room():
    room_data = request.json
    room_label = room_data['room_label']
    building_label = room_data['building_label']
    room_audio = room_data['audio']
    chirp_sample_offset = 0
    counter = 0
    np_arr = np.asarray(room_audio, dtype=np.int16)
    for i in range(chirp_amount - chirp_error_amount):
        start_rate = int(i * interval_rate + chirp_sample_offset)
        sliced = np_arr[0, start_rate:(int(start_rate + interval_rate))]
        create_spectrogram(sliced, 'scipy_images/tarck' + str(counter) + '.jpg')
        counter += 1

    # filename = doc_ref.id + ".wav"
    # write(filename, 44100, arr)

    return 'OK'


@app.route('/')
def hello_world():  # put application's code here
    spectgramCreator = SpectogramCreator()
    letters = ["A", "B", "C", "D", "E"]
    # samplerate, wav_array = wavfile.read('wav_files/EWI_A.wav')
    # np_arr = np.asarray(wav_array, dtype=np.int16)
    # chirp_sample_offset = compute_offset(np_arr)
    # for place in os.listdir("wav_files/"):
    #     if not place.__contains__("EWI"):
    #         continue
    #     samplerate, wav_array = wavfile.read('wav_files/'+place)
    #     np_arr = np.asarray(wav_array[int(4*interval_rate):], dtype=np.int16)
    #     chirp_sample_offset = compute_offset(np_arr)
    #     # print(chirp_sample_offset)
    #     # chirp_sample_offset = 0
    #     # print(chirp_sample_offset)
    #     letter = place.split("_")[1].split(".")[0]
    #     print(letter)
    #     for i in range(int(np_arr.size / interval_rate) - chirp_error_amount):
    #         # if i == 5:
    #         #     start_rate = int((i + 1) * interval_rate + chirp_sample_offset)
    #         #     sliced = np_arr[start_rate:(int(start_rate + interval_rate))]
    #         #     plt.plot(sliced)
    #         #     plt.ylabel("Amplitude")
    #         #     plt.xlabel("Time")
    #         #     # plt.show()
    #         #     plt.savefig("waveplots/"+letter+"_"+str(i)+"_3.png")
    #         #     plt.clf()
    #
    #         start_rate = int((i+1) * interval_rate + chirp_sample_offset)
    #         sliced = np_arr[start_rate:(int(start_rate + interval_rate))]
    #         spectgramCreator.createSpectrogramScipy(letter, sliced, "EWI", i)

    return 'Hello World!'

@app.route('/predict_location')
def predict_location():
    model_name = request.args.get("modelName").replace("-", "_")
    list_of_records = request.data
    dictionary = json.loads(list_of_records)
    # print(dictionary)
    modelCreator = ModelCreator()
    i = 0
    for key in dictionary:
        i += 1
        dictionary[key] = [int(i) for i in dictionary[key].strip('][').split(', ')]
    spectrogramCreator = SpectogramCreator()
    for key in dictionary:
        big_array = dictionary[key][int(0):]
        np_arr = np.asarray(big_array, dtype=np.int16)
        chirp_sample_offset = compute_offset(np_arr)
        for i in range(1):
            # print("Kur")
            start_rate = int(i * interval_rate + chirp_sample_offset)
            sliced = np_arr[start_rate:(int(start_rate + interval_rate))]

            spectrogram = spectrogramCreator.createSpectrogramScipyTest(sliced)
            spectrogram = spectrogram.reshape((1, 5, 32, 1))
            return str(modelCreator.testModel(spectrogram, model_name))

    # print("Hui")
    return 0


@app.route('/train_model_for_building')
def train_model_for_building():
    buildingLabel = request.args.get("buildingLabel")
    # model_to_train = request.args.get("modelToTrain")
    model_name = request.args.get("modelName")
    model_epochs = int(request.args.get("epochs"))
    model_batches = int(request.args.get("batch"))
    body_data = request.data
    model_infos = json.loads(body_data)["models"]

    for model_info in model_infos:
        model_creator = ModelCreator()
        print("Start with "+model_info["model"])
        model_creator.trainModel(model_info["model"], buildingLabel, model_name, model_info, model_epochs, model_batches)
        print("Finish with " + model_info["model"])
    return "Success"


@app.route('/add_new_location_point', methods=['POST'])
def add_new_location_point():
    list_of_records = request.data
    dictionary = json.loads(list_of_records)
    placeLabel = request.args.get("placeLabel")
    buildingLabel = request.args.get("buildingLabel")

    print(placeLabel)
    print(buildingLabel)
    spectgramCreator = SpectogramCreator()
    i = 0
    for key in dictionary:
        i += 1
        dictionary[key] = [int(i) for i in dictionary[key].strip('][').split(', ')]
    chirp_sample_offset = 0
    i = 0
    for key in dictionary:
        big_array = dictionary[key][int(0):]
        np_arr = np.asarray(big_array, dtype=np.int16)
        write("wav_files/"+buildingLabel+"_"+placeLabel+".wav", 44100, np_arr)

    print("Done")
    return "Success"

def compute_offset(np_arr):
    chirp_found = False
    spectgramCreator = SpectogramCreator()
    y = 0
    while True and y < 500:
        # print(i, interval_rate, chirp_sample_offset)
        start_rate = int(y * interval_rate)
        sliced = np_arr[start_rate:(int(start_rate + interval_rate))]
        # print(sliced)
        for i in range(sliced.size):
            if abs(sliced[i]) > 10000:
                print(i-50)
                return i-50
        y+=1

    if chirp_found == False:
        return "Failure"


@app.route('/get_model_names')
def getModelNames():
    model_names = []

    for model_name in listdir("models/dnn_models/"):
        model_names.append("dnn_"+model_name.split(".")[0].replace("-", "_"))

    for model_name in listdir("models/cnn_models/"):
        model_names.append("cnn_"+model_name.split(".")[0].replace("-", "_"))

    for model_name in listdir("models/rnn_models/"):
        model_names.append("rnn_"+model_name.split(".")[0].replace("-", "_"))

    for model_name in listdir("models/knn_models/"):
        model_names.append("knn_"+model_name.split(".")[0].replace("-", "_"))

    for model_name in listdir("models/sgd_models/"):
        model_names.append("sgd_"+model_name.split(".")[0].replace("-", "_"))

    return model_names


@app.route('/load_models')
def initialize_models():
    DNNModel().load_models("models/dnn_models/")
    CNNModel().load_models("models/cnn_models/")
    RNNModel().load_models("models/rnn_models/")
    # DBNModel().load_models("models/dbn_models/")
    KNNModel().load_models("models/knn_models/")
    LinearClassificationModel().load_models("models/sgd_models/")
    return "done"

if __name__ == '__main__':
    app.run(host="192.168.56.1", port=5000, debug=True)

# Train the models again
# Test them with all data sets
# Compute their energy consumption
# Compute the time necessary to make a prediction - send requests from front-end to backend
