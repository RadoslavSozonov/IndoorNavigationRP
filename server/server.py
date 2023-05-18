from flask import Flask, request 
import firebase_admin
from firebase_admin import credentials, firestore
from scipy.io.wavfile import write
from scipy.signal import spectrogram
from scipy.signal.windows import hann
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


APP = Flask(__name__)

cred = credentials.Certificate('key.json')
app = firebase_admin.initialize_app(cred)
db = firestore.client()


interval = 0.1
sample_rate = 44100
chirp_amount = 6
# amount of chirps that are ignored, since some of the last chirps dont work
chirp_error_amount = 2
chirp_sample_offset = 1600

interval_rate = sample_rate * interval

def create_spectrogram(array, filename):
    print(array.shape)
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

    counter = 0
    np_arr = np.asarray(room_audio, dtype=np.int16)
    for i in range(chirp_amount - chirp_error_amount):
        start_rate = int(i * interval_rate + chirp_sample_offset)
        sliced = np_arr[0,start_rate:(int(start_rate + interval_rate))]
        create_spectrogram(sliced, 'tarck' + str(counter) + '.jpg')
        counter += 1
    
    # filename = doc_ref.id + ".wav"
    # write(filename, 44100, arr)


    return 'OK'


@APP.route('/clasify', methods=['POST'])
def calsify_room():
    audio = request.files['audio']
    #TODO: run the clasifier
    result = 'room_1'
    return result

if __name__ == '__main__':
    APP.run(host='0.0.0.0', debug=True)

