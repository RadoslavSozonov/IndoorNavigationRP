from room import Room
from uuid import uuid4
from flask import Flask, request 
import firebase_admin
from firebase_admin import credentials, firestore
from scipy.io.wavfile import write
import numpy as np


APP = Flask(__name__)
UNSAVED_ROOMS = {"1234": Room(None)}

cred = credentials.Certificate('key.json')

app = firebase_admin.initialize_app(cred)

db = firestore.client()


@APP.route('/get_rooms', methods=['GET'])
def get_rooms():
    #TODO: quesry database for all rooms
    room_list = []
    collections = db.collections()
    for collection in collections:
        for document in collection.list_documents():
            room_list.append(document.get().to_dict())
    return room_list

@APP.route('/add_room', methods=['POST', 'GET'])
def add_room():

    if request.method == 'POST':
        #audio = request.files['audio']
        #room = Room(audio)
        #room_uuid = uuid4()
        #UNSAVED_ROOMS.update({room_uuid: room})
        room_data = request.json
        room_label = room_data['room_label']
        building_label = room_data['building_label']
        room_audio = room_data['audio']
        
        
        update_time, doc_ref = db.collection(building_label).add({})
        data = {
            u'building': building_label,
            u'room': room_label,
            #'audio': room_audio
            u'uuid':doc_ref.id
        }
        #write("test.wav", 44100, room_audio.astype(np.int16))
        doc_ref.set(data)

        return 'OK'
        #return room_uuid

    if request.method == 'GET':
        room_data = request.json
        room_uuid = room_data['uuid']
        room_label = room_data['room_label']
        building_label = room_data['building_label']
        #room = UNSAVED_ROOMS[room_uuid]
        #room.set_room_label(room_label)
        #room.set_building_label(building_label)

        #TODO: save new room to the database
        data = {
            u'building': building_label,
            u'room': room_label,
            u'audio': "Work in progress, will probably be a URL to firebase storage OR audio file encoding",
            u'uuid':room_uuid
        }
        db.collection(building_label).document(room_uuid).set(data)



        #UNSAVED_ROOMS.pop(room_uuid)
        return 'OK'

@APP.route('/clasify', methods=['POST'])
def calsify_room():
    audio = request.files['audio']
    #TODO: run the clasifier
    result = 'room_1'
    return result

if __name__ == '__main__':
    APP.run(host='0.0.0.0', debug=True)

