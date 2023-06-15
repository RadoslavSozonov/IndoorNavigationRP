from flask import Flask, request 
import json
from scipy.io import wavfile
from scipy.signal import find_peaks
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")

from SpectogramCreator import SpectogramCreator
from AudioFilter import AudioFilter
from SignalMock import SignalMock
from Database import Database
from Model import Model

APP = Flask(__name__)

spectogramCreator = SpectogramCreator()
audioFilter = AudioFilter()
signalMock = SignalMock()
database = Database()
model = Model()

counter = 0

datafolder = "database\\"

# cnnModel : CNNModel

@APP.route('/', methods=['POST', 'GET'])
def hello_world():
    return "Server is active"

@APP.route('/clear_database', methods=['GET'])
def clear_database():
    database.clear()
    return "Database cleared"

@APP.route('/mock_input', methods=['GET'])
def mock_input():
    sample_name = request.args.get("name")
    echo_delay = float(request.args.get("delay"))
    sound_sample = signalMock.createMockInput(echo_delay)
    pr = float(request.args.get("prominence"))

    handle_input(sound_sample, sample_name, "mock", pr)
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

    return handle_input(sound_sample, placeLabel, buildingLabel, 0.05)

@APP.route('/train_model', methods=['POST', 'GET'])
def train_model():

    data = database.get_json()

    audio_samples = []
    labels = []

    for building in data['Buildings']:
        for room in data['Buildings'][building]:
            for i in range(len(data['Buildings'][building][room]['data'])):
                # load the file and train model using data
                # _, audio_sample = wavfile.read(data['Buildings'][building][room]['data'][i])
                audio_sample = np.load(data['Buildings'][building][room]['data'][i])

                print(len(audio_sample))

                audio_samples.append(audio_sample)
                labels.append(data['Buildings'][building][room]['ID'])

    # print(labels)
    model.train(audio_samples, labels)

    return "model trained"

@APP.route('/classify', methods=['POST'])
def classify():
    list_of_records = request.data
    dictionary = json.loads(list_of_records)

    for key in dictionary:
        dictionary[key] = [float(i) for i in dictionary[key].strip('][').split(', ')]

    sound_sample = dictionary['recording']

    sound_sample = np.array(sound_sample, dtype=np.float32)

    normalized_sample = (sound_sample - np.mean(sound_sample)) / np.std(sound_sample)
    prediction = model.predict(np.expand_dims(normalized_sample, axis=0))
    predicted_label = model.id_to_label[np.argmax(prediction)]
    print(f'Predicted Label: {predicted_label}')
    return predicted_label

def handle_input(sound_sample, room, building, pr):
    sound_sample = np.asarray(sound_sample, dtype=np.float32)

    # sound_sample = audioFilter.apply_high_pass_filter(sound_sample, 18500)

    cutoffs = find_cutoffs(sound_sample, pr)

    spectogramCreator.generate_black_white_spectogram(sound_sample, filename(building, room, "SPECT"))

    cnt = 0
    for i in range(1, len(cutoffs), 2):
        sub_sample = sound_sample[cutoffs[i-1]:cutoffs[i]]

        spectogramCreator.generate_black_white_spectogram(sub_sample, filename(building, room, "SPECT_"+str(cnt)))
        # spectogramCreator.generate_mfccs_spectrogram(sound_sample[peaks[i-1]:peaks[i] - 400], filename(building, room, "MFCCS_"+str(i)))
        # spectogramCreator.generate_chroma_spectrogram(sound_sample[peaks[i-1]:peaks[i] - 400], filename(building, room, "CHROMA_"+str(i)))
        spectogramCreator.generate_spect(sub_sample, filename(building, room, "BW_SPECT_"+str(cnt)))

        cnt += 1

    print("OK")
    return "Success"

def find_cutoffs(sound_sample, pr):
    sound_sample = audioFilter.apply_high_pass_filter(sound_sample, 18500)
    enveloped = audioFilter.smooth(audioFilter.envelope(sound_sample))
    peaks, _ = find_peaks(enveloped, prominence=pr)

    plt.clf()
    plt.figure(figsize=(30, 5))

    cutoffs = []
    for i in range(1, len(peaks)):
        cutoffs.append(peaks[i-1] + 600)
        cutoffs.append(peaks[i] - 400)

        # plt.axvline(x=peaks[i-1] + 600, color='red')
        # plt.axvline(x=peaks[i] - 400, color='red')

    plt.plot(sound_sample)
    plt.plot(peaks, enveloped[peaks], "x")
    plt.savefig(filename("", "", "ENVELOPED_PEAKS"))

    return cutoffs

def filename(building, room, ID):
    return datafolder + 'B(' + building + ')_R('+room+')_'+ID+'.png'

if __name__ == '__main__':
    APP.run(host='0.0.0.0', debug=True)