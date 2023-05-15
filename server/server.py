from flask import Flask, request 
import firebase_admin
from firebase_admin import credentials, firestore
from scipy.io.wavfile import write
from scipy.signal import spectrogram
from scipy.signal.windows import hann
import numpy as np
import matplotlib.pyplot as plt


APP = Flask(__name__)

cred = credentials.Certificate('key.json')
app = firebase_admin.initialize_app(cred)
db = firestore.client()


def create_spectrogram(array, filename):
    f, t, Sxx = spectrogram(array, 44100, window=hann(256, sym=False))
    plt.pcolormesh(t, f, Sxx, shading='gouraud')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.savefig(filename)

@APP.route('/get_rooms', methods=['GET'])
def get_rooms():
    room_list = []
    response_body = {}
    collections = db.collections()
    for collection in collections:
        for document in collection.list_documents():
            room_list.append(document.get().to_dict()["room"])
        response_body.update({collection.id: room_list})
        room_list = []

    return response_body

@APP.route('/add_room', methods=['POST'])
def add_room():

    room_data = request.json
    room_label = room_data['room_label']
    building_label = room_data['building_label']
    room_audio = room_data['audio']
    
    
    update_time, doc_ref = db.collection(building_label).add({})
    data = {
        u'building': building_label,
        u'room': room_label,
        u'audio': "Currently stored locally",
        u'uuid':doc_ref.id
    }

    doc_ref.update(data)

    filename = doc_ref.id + ".wav"
    concatenatedAudio = sum(room_audio, [])
    arr = np.asarray(concatenatedAudio).astype(np.int16)

    counter = 0
    for track in room_audio:
        create_spectrogram(np.asarray(track), 'tarck' + str(counter) + '.jpg')
        counter += 1
    
    write(filename, 44100, arr)


    return 'OK'


@APP.route('/clasify', methods=['POST'])
def calsify_room():
    audio = request.files['audio']
    #TODO: run the clasifier
    result = 'room_1'
    return result

if __name__ == '__main__':
    APP.run(host='0.0.0.0', debug=True)

