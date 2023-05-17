from flask import Flask, request 
import firebase_admin
from firebase_admin import credentials, firestore
from scipy.io.wavfile import write
from scipy.signal import spectrogram
from scipy.signal.windows import hann
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mtplt
import json
import tensorflow as tf
mtplt.use('Agg')

from ModelCreator import ModelCreator
from SpectogramCreator import SpectogramCreator
from DeepModels.CNNModel import CNNModel

APP = Flask(__name__)

cred = credentials.Certificate('key.json')
app = firebase_admin.initialize_app(cred)
db = firestore.client()

counter = 0

cnnModel : CNNModel

@APP.route('/add_new_location_point', methods=['POST'])
def add_new_location_point():
    print("adding room...")

    list_of_records = request.data
    dictionary = json.loads(list_of_records)
    placeLabel = request.args.get("placeLabel")
    buildingLabel = request.args.get("buildingLabel")

    spectgramCreator = SpectogramCreator()
    i = 0
    for key in dictionary:
        i+=1
        dictionary[key] = [int(i) for i in dictionary[key].strip('][').split(', ')]

    for key in dictionary:
        print("length: " + str(len(dictionary[key])))
        big_array = dictionary[key]
        for i in range(int(len(big_array)/4410)-1):
            if i == 0:
                continue
            spectgramCreator.createSpectogram(placeLabel, [big_array[(i)*4410:(i+1)*4410]], buildingLabel, i+1)
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
    APP.run(host='192.168.56.1', debug=True)