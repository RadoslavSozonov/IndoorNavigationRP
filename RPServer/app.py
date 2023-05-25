from flask import Flask, request
import json
import numpy as np
from scipy.io import wavfile
from matplotlib import pyplot as plt
from scipy.signal import spectrogram
from scipy.signal.windows import hann

from ModelCreator import ModelCreator
from SpectogramCreator import SpectogramCreator

app = Flask(__name__)

interval = 0.1
sample_rate = 44100
chirp_amount = 24
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


@app.route('/add_room', methods=['POST'])
def add_room():
    room_data = request.json
    room_label = room_data['room_label']
    building_label = room_data['building_label']
    room_audio = room_data['audio']

    # update_time, doc_ref = db.collection(building_label).add({})
    # data = {
    #     u'building': building_label,
    #     u'room': room_label,
    #     u'audio': "Currently stored locally",
    #     u'uuid': doc_ref.id
    # }
    #
    # doc_ref.update(data)
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

    samplerate, wav_array = wavfile.read('wavfile.wav')
    np_arr = np.asarray(wav_array[0], dtype=np.int16)

    start_rate = 0
    sliced = np_arr[start_rate:(int(start_rate + interval_rate))]

    chirp_sample_offset = spectgramCreator.get_offset(sliced)
    for i in range(int(len(wav_array[0]) / interval_rate) - chirp_error_amount):
        start_rate = int(i * interval_rate + chirp_sample_offset)
        sliced = np_arr[start_rate:(int(start_rate + interval_rate))]
        spectgramCreator.createSpectogram("placeLabel", sliced, "buildingLabel", i + 1)
    return 'Hello World!'


@app.route('/train_model_for_building')
def train_model_for_building():
    buildingLabel = request.args.get("buildingLabel")
    model_to_train = request.args.get("modelToTrain")
    model_name = request.args.get("modelName")
    body_data = request.data
    model_info = json.loads(body_data)
    model_creator = ModelCreator()
    model_creator.trainModel(model_to_train, buildingLabel, model_name, model_info)
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
    for key in dictionary:
        big_array = dictionary[key][int(chirp_error_amount * interval_rate):]
        np_arr = np.asarray(big_array, dtype=np.int16)

        # while True:
        #     print(i, interval_rate, chirp_sample_offset)
        #     start_rate = int(i * interval_rate)
        #     sliced = np_arr[start_rate:(int(start_rate + interval_rate))]
        #
        #     chirp_sample_offset = spectgramCreator.get_offset(sliced)
        #     if chirp_sample_offset is not None and chirp_sample_offset > 0:
        #         break
        #     i += 1

        for i in range(int(len(big_array) / interval_rate) - chirp_error_amount):
            start_rate = int(i * interval_rate + chirp_sample_offset)
            sliced = np_arr[start_rate:(int(start_rate + interval_rate))]
            spectgramCreator.createSpectogram(placeLabel, sliced, buildingLabel, i + 1)
    # print(dictionary)
    print("Done")
    return "Success"


if __name__ == '__main__':
    app.run(host="192.168.56.1", port=5000, debug=True)

'''
Example request to train model and body:
http://192.168.56.1:5000/train_model_for_building?buildingLabel=Kloost226&modelToTrain=cnn&modelName=my_first_nn
    
{
    "conv_layers": [
        {
            "conv_filters": 16,
            "conv_activation_func": "relu",
            "conv_layer_filter_size": 4,
            "pool_layer_filter_size": 2,
            "layer_num": 1
        },
        {
            "conv_filters": 32,
            "conv_activation_func": "relu",
            "conv_layer_filter_size": 4,
            "pool_layer_filter_size": 2,
            "layer_num": 2
        }
    ],
    "dense_layers": [
        {
            "units": 1024,
            "activation_func": "relu"
        }
    ]
}
    
'''
