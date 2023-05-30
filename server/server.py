from flask import Flask, request 
from database import LocalDatabase
from scipy.io.wavfile import write
from scipy.io.wavfile import read
import cv2
from scipy.signal import spectrogram
from scipy.signal.windows import hann
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import time
import os

from datetime import datetime



APP = Flask(__name__)
db = LocalDatabase()

interval = 0.1
sample_rate = 44100
chirp_amount = 200
# amount of chirps that are ignored, since some of the last chirps dont work
chirp_last_error = 3
chirp_first_error = 1
good_chirp_amount = chirp_amount - chirp_last_error - chirp_first_error
chirp_radius = 0.016

interval_samples = sample_rate * interval
chirp_radius_samples = int(sample_rate * chirp_radius/2)


min_frequency = 19500
max_frequency = 20500


def find_first_chirp(arr):
    # Scan at most the first interval for the first chirp
    sliced_arr = arr[:int(interval_samples)]
    f, t, Sxx = spectrogram(sliced_arr, 44100, window=hann(256, sym=False))
    # Only handle high frequencies
    high_frequency_indices = np.where((f > min_frequency) & (f < max_frequency))
    Sxx = Sxx[high_frequency_indices]

    # Calculate the highest point of intensity to find the chirp
    end_of_chirps = np.argmax(Sxx, axis=1)

    counts = np.bincount(end_of_chirps)
    chirp_cut_off = np.argmax(counts)
    time_of_cut_off = t[chirp_cut_off]

    # f = f[high_frequency_indices]
    # t = t[chirp_cut_off:]
    # Sxx = Sxx[:,chirp_cut_off:]
    # # extract the maximum
    # plt.pcolormesh(t, f, Sxx, shading='gouraud')
    # plt.ylabel('Frequency [Hz]')
    # plt.xlabel('Time [sec]')
    # plt.savefig("Test.jpg")
    # Returns at which point in the sample is the center of the chirp
    return int(time_of_cut_off * sample_rate )


def create_spectrogram(array, filename):
    f, t, Sxx = spectrogram(array, 44100, window=hann(256, sym=False))
    high_frequency_indices = np.where((f > min_frequency) & (f < max_frequency))
    f = f[high_frequency_indices]
    Sxx = Sxx[high_frequency_indices]

    # Plot the spectrogram and save it
    plt.pcolormesh(t, f, Sxx, shading='gouraud')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.savefig(filename)

    # Clear the plot
    plt.clf()

    # After saving, read the image and extract the graph from the figure
    time.sleep(0.1)
    rgb = cv2.imread(filename)
    rgb = rgb[59:428, 80:579]
    rgb = cv2.resize(rgb, (32, 5))
    not_rgb = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(filename, not_rgb)

    return rgb


@APP.route('/get_rooms', methods=['GET'])
def get_rooms():

    return db.get_buildings_with_rooms()

@APP.route('/add_room', methods=['POST'])
def add_room():

    room_data = request.json
    room_label = room_data['room_label']
    building_label = room_data['building_label']
    room_audio = room_data['audio']

    today = datetime.now()
    classify_date = today.strftime("%b-%d-%Y-%H-%M-%S")


    np_arr = np.asarray(room_audio, dtype=np.int16)
    training_set_directory = './images/'+ str(building_label) + '/' + str(room_label)
    if not os.path.exists(training_set_directory):
        # Create a new directory because it does not exist
        os.makedirs(training_set_directory)

    # Cut out all the bad chirps
    np_arr = np_arr[0, int(chirp_first_error * interval_samples): int((chirp_amount - chirp_last_error) * interval_samples)]
    # Find the first chirp in the audio file and offset everything
    first_chirp_offset = find_first_chirp(np_arr)
    for i in range(good_chirp_amount):
        # calculates the interval, and applied the chirp offset, to eliminate the emitted chirp and only process the echos
        start_rate = int(i * interval_samples + first_chirp_offset + chirp_radius_samples )
        # cuts out the ending chirp
        end_rate = int((i + 1) * interval_samples + first_chirp_offset - chirp_radius_samples  )
        sliced = np_arr[start_rate : end_rate]
        create_spectrogram(sliced, training_set_directory+ '/' + classify_date + '-' + str(i) + '.png')
    

    # write(doc_ref.id + ".wav", sample_rate, np_arr.astype(np.int16))
    return 'OK'


@APP.route('/recognize_room', methods=['POST'])
def calsify_room():
    room_data = request.json
    room_label = room_data['room_label']
    building_label = room_data['building_label']
    room_audio = room_data['audio']
    #TODO: run the clasifier
    result = 'room_1'
    return result

if __name__ == '__main__':
    APP.run(host='0.0.0.0', debug=True)


