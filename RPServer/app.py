from flask import Flask, request
import json
from ModelCreator import ModelCreator
from SpectogramCreator import SpectogramCreator

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/train_model_for_building')
def train_model_for_building():
    buildingLabel = request.args.get("buildingLabel")
    model_to_train = request.args.get("modelToTrain")
    model_creator = ModelCreator()
    model_creator.trainModel(model_to_train, buildingLabel)
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
        i+=1
        dictionary[key] = [int(i) for i in dictionary[key].strip('][').split(', ')]

    for key in dictionary:
        big_array = dictionary[key]
        # print(len(big_array)/4410)
        for i in range(int(len(big_array)/4410)-1):
            if i == 0:
                continue
            spectgramCreator.createSpectogram(placeLabel, [big_array[(i)*4410:(i+1)*4410]], buildingLabel, i+1)
    # print(dictionary)
    return "Success"



if __name__ == '__main__':
    app.run(host="192.168.56.1", port=5000, debug=True)
