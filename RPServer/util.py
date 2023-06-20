import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import os
import time

from scipy.signal import find_peaks
from AudioFilter import AudioFilter
from Database import Database
from Model import Model

import globals

matplotlib.use("Agg")

audioFilter = AudioFilter()
database = Database()
model = Model()

datafolder = "database\\"

def get_numerical_sound_sample(request_data):
    for key in request_data:
        request_data[key] = [float(i) for i in request_data[key].strip('][').split(', ')]

    sound_sample = request_data['1']
    return sound_sample

def handle_input(sound_sample, room, building):
    sound_sample = np.asarray(sound_sample, dtype=np.float32)

    

    cutoffs = find_cutoffs(sound_sample)

    # sound_sample = audioFilter.apply_high_pass_filter(sound_sample, 18500)

    for i in range(1, len(cutoffs), 2):
        sub_sample = sound_sample[cutoffs[i-1]:cutoffs[i]]

        database.put(building, room, sub_sample)

    print("OK")
    return "Success"

def find_cutoffs(sound_sample):
    sound_sample = audioFilter.apply_high_pass_filter(sound_sample, 19500)
    enveloped = audioFilter.smooth(audioFilter.envelope(sound_sample))
    peaks, _ = find_peaks(enveloped, prominence=0.005)

    plt.clf()
    plt.figure(figsize=(30, 5))

    cutoffs = []
    for i in range(1, len(peaks)):
        cutoffs.append(peaks[i-1] + 220)
        cutoffs.append(peaks[i] - 300)

    #     plt.axvline(x=peaks[i-1] + 220, color='red')
    #     plt.axvline(x=peaks[i] - 300, color='red')

    # plt.plot(enveloped)
    # plt.plot(peaks, enveloped[peaks], "x")
    # plt.savefig(filename("", "", "ENVELOPED_PEAKS"))

    return cutoffs

def filename(building, room, ID):
    return datafolder + 'B(' + building + ')_R('+room+')_'+ID+'.png'


def _train_model():
    print("training model")

    for type in globals.SPECTROGRAM_TYPES:
        data, labels, label_amount = database.get_all(type)

        model.train(data, labels, label_amount, type)

    return

def _classify(sound_sample):
    sound_sample = np.array(sound_sample, dtype=np.float32)

    model.load()

    cutoffs = find_cutoffs(sound_sample)

    predictions = []

    for i in range(1, len(cutoffs), 2):
        sub_sample = sound_sample[cutoffs[i-1]:cutoffs[i]]

        normalized_sample = (sub_sample - np.mean(sub_sample)) / np.std(sub_sample)

        filename = "temp\\" + str(len(os.listdir("temp\\")))

        database.create_spectrogram(normalized_sample, filename)

        time.sleep(0.1)

        data = database.load_image(filename + ".png")

        prediction = model.predict(np.expand_dims(data, axis=0))
        predictions.append(model.id_to_label[np.argmax(prediction)])
    
    print(predictions)
    return "predicted_label"