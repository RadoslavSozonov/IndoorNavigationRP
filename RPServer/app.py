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

APP = Flask(__name__)

spectogramCreator = SpectogramCreator()
audioFilter = AudioFilter()
signalMock = SignalMock()

counter = 0

# cnnModel : CNNModel

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

def handle_input(sound_sample, placeLabel, buildingLabel):
    filtered_sample =  audioFilter.apply_high_pass_filter(sound_sample, 14000)
    enveloped = audioFilter.envelope(filtered_sample)

    enveloped = audioFilter.smooth(enveloped)

    spectogramCreator.generate_audio_graph(enveloped, 'plot_building_' + buildingLabel + '_room_'+placeLabel+'_.png')

    frequencies, power_spectrum = sps.periodogram(filtered_sample)
    plt.figure()
    plt.plot(frequencies, power_spectrum)
    plt.xlabel('Frequency')
    plt.ylabel('Power Spectrum')
    plt.title('Periodogram Analysis')
    plt.grid(True)
    plt.savefig("periodogram.png")

    # spectogramCreator.generate_spectogram(output_signal, 'plot_building_' + buildingLabel + '_room_'+placeLabel+'_SPECT.png')

    # spectogramCreator.generate_alternative_spectogram(output_signal, 'plot_building_' + buildingLabel + '_room_'+placeLabel+'_SPECTALT.png')

    # spectogramCreator.generate_black_white_spectogram(filtered_sample, 'plot_building_' + buildingLabel + '_room_'+placeLabel+'_SPECT_BW.png')

    spectogramCreator.generate_fourier_graph(filtered_sample, 'plot_building_' + buildingLabel + '_room_'+placeLabel+'_FOURIER.png')

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

if __name__ == '__main__':
    APP.run(host='0.0.0.0', debug=True)