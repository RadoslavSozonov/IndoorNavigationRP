from room import Room
from uuid import uuid4
from flask import Flask, request 

APP = Flask(__name__)
UNSAVED_ROOMS = {"1234": Room(None)}

@APP.route('/get_rooms', methods=['GET'])
def get_rooms():
    #TODO: quesry database for all rooms
    room_list = []
    return room_list

@APP.route('/add_room', methods=['POST', 'GET'])
def add_room():

    if request.method == 'POST':
        audio = request.files['audio']
        room = Room(audio)
        room_uuid = uuid4()
        UNSAVED_ROOMS.update({room_uuid: room})
        return room_uuid

    if request.method == 'GET':
        room_data = request.json
        room_uuid = room_data['uuid']
        room_label = room_data['room_label']
        building_label = room_data['building_label']
        room = UNSAVED_ROOMS[room_uuid]
        room.set_room_label(room_label)
        room.set_building_label(building_label)

        #TODO: save new room to the database
        UNSAVED_ROOMS.pop(room_uuid)
        return 'OK'

@APP.route('/clasify', methods=['POST'])
def calsify_room():
    audio = request.files['audio']
    #TODO: run the clasifier
    result = 'room_1'
    return result

if __name__ == '__main__':
    APP.run(host='0.0.0.0', debug=True)

