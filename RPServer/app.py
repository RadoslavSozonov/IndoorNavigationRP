from os import listdir

from flask import Flask, request
import json
from scipy.io.wavfile import write
from Converter import Converter
from DataLoader import DataLoader
from DeepModels.CNNModel import CNNModel
from DeepModels.DNNModel import DNNModel
from DeepModels.RNNModel import RNNModel
from ModelCreator import ModelCreator

app = Flask(__name__)

interval = 0.1
sample_rate = 44100
chirp_amount = 204
# amount of chirps that are ignored, since some of the last chirps dont work
chirp_error_amount = 2
# chirp_sample_offset = 0

interval_rate = sample_rate * interval


@app.route('/convert_wav_to_spectrograms')
def convert_wav_to_spectrograms():
    data_set = request.args.get("dataset")
    Converter().convert_wav_to_spectrograms(data_set)
    return "Done"


@app.route('/convert_wav_to_text_file')
def convert_wav_to_text_file():
    data_set = request.args.get("dataset")
    Converter().convert_wav_to_text_file(data_set)
    return "Done"


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route("/play_ground")
def play_ground():
    return "Done"


@app.route('/load_data_db')
def load_data_db():  # put application's code here
    data_building = request.args.get("building_name")
    DataLoader().load_data_in_db_from_wav_file(data_building)
    return 'Loaded!'


@app.route('/evaluate')
def evaluate():
    model_name = request.args.get("model")
    data_set = request.args.get("dataset")
    ModelCreator().evaluate(model_name=model_name, data_set=data_set)
    return "Done"


@app.route('/predict_location')
def predict_location():
    model_name = request.args.get("modelName").replace("-", "_")
    list_of_records = request.data
    dictionary = json.loads(list_of_records)
    return ModelCreator.predict_location(model_name, dictionary)


@app.route('/train_model_for_building')
def train_model_for_building():
    buildingLabel = request.args.get("buildingLabel")
    # model_to_train = request.args.get("modelToTrain")
    model_name = request.args.get("modelName")
    model_epochs = int(request.args.get("epochs"))
    model_batches = int(request.args.get("batch"))
    body_data = request.data
    model_infos = json.loads(body_data)["models"]

    for model_info in model_infos:
        model_creator = ModelCreator()
        print("Start with "+model_info["model"])
        model_creator.trainModel(model_info["model"], buildingLabel, model_info, model_epochs, model_batches)
        print("Finish with " + model_info["model"])
    return "Success"


@app.route('/add_new_location_point', methods=['POST'])
def add_new_location_point():
    list_of_records = request.data
    dictionary = json.loads(list_of_records)
    placeLabel = request.args.get("placeLabel")
    buildingLabel = request.args.get("buildingLabel")

    np_arr = Converter().json_to_audio_data_converter(dictionary)
    DataLoader().load_data_in_db(buildingLabel, placeLabel, np_arr)
    write("wav_files/"+buildingLabel+"_"+placeLabel+".wav", 44100, np_arr)
    print(f"Location Added {buildingLabel} {placeLabel}")
    return "Success"


@app.route('/get_model_names')
def getModelNames():
    model_names = []

    for model_name in listdir("models/dnn_models/"):
        model_names.append("dnn_"+model_name.split(".")[0].replace("-", "_"))

    for model_name in listdir("models/cnn_models/"):
        model_names.append("cnn_"+model_name.split(".")[0].replace("-", "_"))

    for model_name in listdir("models/rnn_models/"):
        model_names.append("rnn_"+model_name.split(".")[0].replace("-", "_"))

    for model_name in listdir("models/knn_models/"):
        model_names.append("knn_"+model_name.split(".")[0].replace("-", "_"))

    for model_name in listdir("models/sgd_models/"):
        model_names.append("sgd_"+model_name.split(".")[0].replace("-", "_"))

    return model_names


@app.route('/load_models')
def initialize_models():
    DNNModel().load_models("models/dnn_models/")
    CNNModel().load_models("models/cnn_models/")
    RNNModel().load_models("models/rnn_models/")
    return "done"

@app.route('/compress_models')
def compress_models():
    DNNModel().compress("models/dnn_models/")
    CNNModel().compress("models/cnn_models/")
    RNNModel().compress("models/rnn_models/")
    return "done"

if __name__ == '__main__':
    app.run(host="192.168.56.1", port=5000, debug=True)
