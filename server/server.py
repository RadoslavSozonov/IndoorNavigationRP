from flask import Flask, request 
from database import LocalDatabase
from data_handling import find_first_chirp, create_spectrogram, create_training_set, create_single_echo
from acoustic_classifier import AcousticClassifier
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
db = LocalDatabase()
acoustic_model = AcousticClassifier()


@APP.route('/get_rooms', methods=['GET'])
def get_rooms():
    return db.get_buildings_with_rooms()


@APP.route('/train', methods=['GET'])
def train_model():
    acoustic_model.train(0.8)
    return "Done!"


@APP.route('/add_room', methods=['POST'])
def add_room():

    room_data = request.json
    room_label = room_data['room_label']
    building_label = room_data['building_label']
    room_audio = room_data['audio']

    np_arr = np.asarray(room_audio, dtype=np.int16)
    # Cut out all the bad chirps
    np_arr = np_arr[0, int(constants.chirp_first_error * constants.interval_samples): int((constants.chirp_amount - constants.chirp_last_error) * constants.interval_samples)]

    # Create the dataset
    create_training_set(np_arr, building_label, room_label)

    return 'OK'


@APP.route('/recognize_room', methods=['POST'])
def recognize_room():
    room_data = request.json
    room_audio = room_data['audio']
    np_arr = np.asarray(room_audio, dtype=np.int16)
    np_arr = np_arr[0, int(constants.chirp_first_error * constants.interval_samples): int((constants.recognize_chirp_amount - constants.chirp_last_error) * constants.interval_samples)]
    
    filename = create_single_echo(np_arr)
    time.sleep(0.1)
    result = acoustic_model.classify(db.get_grayscale_image(filename))
    return result

if __name__ == '__main__':
    APP.run(host='0.0.0.0', debug=True)


