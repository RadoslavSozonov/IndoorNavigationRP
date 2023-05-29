from flask import Flask, request 
# import firebase_admin
# from firebase_admin import credentials, firestore
from scipy.io.wavfile import write
from scipy.signal import spectrogram
from scipy.signal.windows import hann
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mtplt
import json
import tensorflow as tf
mtplt.use('Agg')

import wave

from ModelCreator import ModelCreator
from SpectogramCreator import SpectogramCreator
from DeepModels.CNNModel import CNNModel

APP = Flask(__name__)

# cred = credentials.Certificate('key.json')
# app = firebase_admin.initialize_app(cred)
# db = firestore.client()

counter = 0

cnnModel : CNNModel

@APP.route('/add_new_location_point', methods=['POST'])
def add_new_location_point():
    print("adding room...")

    list_of_records = request.data
    dictionary = json.loads(list_of_records)
    placeLabel = request.args.get("placeLabel")
    buildingLabel = request.args.get("buildingLabel")

    for key in dictionary:
        dictionary[key] = [float(i) for i in dictionary[key].strip('][').split(', ')]

    intlist = dictionary['1']

    # print(dictionary)
    # print(intlist[1000:1100])
    
    # filter intlist
    # intlist = np.convolve(intlist, np.ones(2) / 2, mode='valid')

    duration = len(intlist)/44100  # Duration of the audio
    x = np.linspace(0, duration, len(intlist))

    plt.figure(figsize=(25, 5))
    plt.plot(x, intlist)
    plt.xlabel("sample")
    plt.ylabel("amplitude")
    plt.xlim(0, duration)
    plt.title("Recording")
    plt.savefig('plot_building_' + buildingLabel + '_room_'+placeLabel+'_.png')

    # spectgramCreator = SpectogramCreator()

    # for key in dictionary:
    #     print("length: " + str(len(dictionary[key])))
    #     big_array = dictionary[key]
    #     for i in range(int(len(big_array)/4410)-1):
    #         if i == 0:
    #             continue
    #         spectgramCreator.createSpectogram(placeLabel, [big_array[(i)*4410:(i+1)*4410]], buildingLabel, i+1)
    return "Success"

@APP.route('/train_model_for_building')
def train_model_for_building():
    print("training model")
    buildingLabel = request.args.get("buildingLabel")
    model_to_train = request.args.get("modelToTrain")
    model_creator = ModelCreator()

    global cnnModel
    cnnModel = model_creator.trainModel(model_to_train, buildingLabel)
    return "Success"

@APP.route('/classify', methods=['POST'])
def clasify_room():
    print("predicting room....")
    #get the recorded audio
    data = json.loads(request.data)
    spectgramCreator = SpectogramCreator()

    data["recording"] = [int(i) for i in data["recording"].strip('][').split(', ')]

    print(len(data["recording"]))

    #convert data to spectogram, this is where is still goes wrong
    spectogram = spectgramCreator.createSpectogram("", data["recording"], "", 0)

    predicted_label = cnnModel.predict("my_first_model", spectogram)

    print("predicted label: " + predicted_label)

    return predicted_label

if __name__ == '__main__':
    APP.run(host='0.0.0.0', debug=True)