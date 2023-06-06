from flask import Flask, request 
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mtplt
import json
import scipy.signal as sps

mtplt.use('Agg')

import wave

# from ModelCreator import ModelCreator
from SpectogramCreator import SpectogramCreator
# from DeepModels.CNNModel import CNNModel
from AudioFilter import AudioFilter
from SignalMock import SignalMock
from Database import Database

APP = Flask(__name__)

spectogramCreator = SpectogramCreator()
audioFilter = AudioFilter()
signalMock = SignalMock()
database = Database()

counter = 0

datafolder = "database\\"

# cnnModel : CNNModel

@APP.route('/clear_database', methods=['GET'])
def clear_database():
    database.clear()
    return "Database cleared"

@APP.route('/mock_input', methods=['GET'])
def mock_input():
    sample_name = request.args.get("name")
    echo_delay = float(request.args.get("delay"))
    sound_sample = signalMock.createMockInput(echo_delay)

    handle_input(sound_sample, sample_name, "mock")
    return "added " + sample_name

@APP.route('/add_new_location_point', methods=['POST'])
def add_new_location_point():
    print("adding room...")

    list_of_records = request.data
    dictionary = json.loads(list_of_records)
    placeLabel = request.args.get("placeLabel")
    buildingLabel = request.args.get("buildingLabel")

    for key in dictionary:
        dictionary[key] = [float(i) for i in dictionary[key].strip('][').split(', ')]

    sound_sample = dictionary['1']

    return handle_input(sound_sample, placeLabel, buildingLabel)

def handle_input(sound_sample, room, building):
    filtered_sample =  audioFilter.apply_high_pass_filter(sound_sample, 9000)
    # enveloped = audioFilter.smooth(audioFilter.envelope(filtered_sample))

    duration = 3
    cnt = 0
    window = duration * 44100
    for i in range(0, len(filtered_sample) - window,  window):
        fy = spectogramCreator.generate_fourier_graph(filtered_sample[i: i+window], filename(building, room, "FOURIER_"+str(cnt)), False)
        # ADD TO DATABASE
        database.save_image(building, room, fy)
        cnt += 1

    print("added room!")
    return "Success"

# @APP.route('/train_model_for_building')
# def train_model_for_building():
#     print("training model")
#     buildingLabel = request.args.get("buildingLabel")
#     model_to_train = request.args.get("modelToTrain")
#     model_creator = ModelCreator()

#     global cnnModel
#     cnnModel = model_creator.trainModel(model_to_train, buildingLabel)
#     return "Success"

# @APP.route('/classify', methods=['POST'])
# def clasify_room():
#     print("predicting room....")
#     #get the recorded audio
#     data = json.loads(request.data)
#     spectgramCreator = SpectogramCreator()

#     data["recording"] = [int(i) for i in data["recording"].strip('][').split(', ')]

#     print(len(data["recording"]))

#     #convert data to spectogram, this is where is still goes wrong
#     spectogram = spectgramCreator.createSpectogram("", data["recording"], "", 0)

#     predicted_label = cnnModel.predict("my_first_model", spectogram)

#     print("predicted label: " + predicted_label)

#     return predicted_label

def filename(building, room, ID):
    return datafolder + 'B(' + building + ')_R('+room+')_'+ID+'.png'

if __name__ == '__main__':
    APP.run(host='0.0.0.0', debug=True)