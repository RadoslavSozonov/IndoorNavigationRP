from flask import Flask, request 
from data_handling import find_first_chirp, create_spectrogram, create_training_set, create_wifi_training_set, train_classifiers, get_rooms_from_db, multi_classify
from scipy.io.wavfile import write
from scipy.io.wavfile import write
from scipy.signal import spectrogram
from scipy.signal.windows import hann

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import time
import os
import constants
import cv2

matplotlib.use('Agg')


APP = Flask(__name__)




@APP.route('/get_rooms', methods=['GET'])
def get_rooms():
    return get_rooms_from_db()


@APP.route('/train', methods=['GET'])
def train_model():
    train_classifiers()
    return "Done!"


@APP.route('/add_room', methods=['POST'])
def add_room():

    room_data = request.json
    room_label = room_data['room_label']
    building_label = room_data['building_label']
    room_audio = room_data['audio']
    wifi_list = room_data['wifi_list']
    

    np_arr = np.asarray(room_audio, dtype=np.int16)
    # Cut out all the bad chirps
    np_arr = np_arr[0, int(constants.chirp_first_error * constants.interval_samples): int((constants.chirp_amount - constants.chirp_last_error) * constants.interval_samples)]

    # Create the dataset
    create_training_set(np_arr, building_label, room_label)

    create_wifi_training_set(wifi_list, building_label, room_label)

    return 'OK'


@APP.route('/recognize_room', methods=['POST'])
def recognize_room():
    room_data = request.json
    room_audio = room_data['audio']
    wifi_list = room_data['wifi_list'][0]['list']
    np_arr = np.asarray(room_audio, dtype=np.int16)
    np_arr = np_arr[0, int(constants.chirp_first_error * constants.interval_samples): int((constants.recognize_chirp_amount - constants.chirp_last_error) * constants.interval_samples)]

    return multi_classify(np_arr, wifi_list)

if __name__ == '__main__':
    APP.run(host='0.0.0.0', debug=True)


