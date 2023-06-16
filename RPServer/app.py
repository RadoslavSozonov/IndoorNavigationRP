from util import get_numerical_sound_sample, handle_input, _train_model, _classify
from flask import Flask, request 
import json

import numpy as np

from SignalMock import SignalMock
from Database import Database

APP = Flask(__name__)

signalMock = SignalMock()
database = Database()

counter = 0



# cnnModel : CNNModel

@APP.route('/', methods=['POST', 'GET'])
def hello_world():
    return "Server is active"

@APP.route('/clear_database', methods=['GET'])
def clear_database():
    database.clear()
    return "Database cleared"

@APP.route('/add_new_location_point', methods=['POST'])
def add_new_location_point():
    print("adding room...")

    placeLabel = request.args.get("placeLabel")
    buildingLabel = request.args.get("buildingLabel")

    sound_sample = get_numerical_sound_sample(json.loads(request.data))

    return handle_input(sound_sample, placeLabel, buildingLabel, 0.005)

@APP.route('/train_model', methods=['POST', 'GET'])
def train_model():

    _train_model()

    return "model trained"

@APP.route('/classify', methods=['POST'])
def classify():

    sound_sample = get_numerical_sound_sample(request.data)

    return _classify(sound_sample)
    

if __name__ == '__main__':
    APP.run(host='0.0.0.0', debug=True)