import firebase_admin
from firebase_admin import credentials, firestore
from pymongo import MongoClient
import uuid
import numpy as np


cred = credentials.Certificate("key.json")
app = firebase_admin.initialize_app(cred)
database = firestore.client()

client = MongoClient('localhost', 27017)
db = client["RPServer"]



def upload_to_real_time_database(label_building, label_room, spectgram):
    # print("Hi")
    collection = db[label_building]
    dictionary = {}
    for i in range(len(spectgram)):
        # print(type(spectgram[i]))
        dictionary[str(i)] = spectgram[i].tolist()
    collection.insert_one({
        "label_building": label_building,
        "label_room": label_room,
        "data": dictionary
    })
    # database.collection(label_building).document(label_room).set({str(uuid.uuid4()): dictionary}, merge=True)


def get_from_real_time_database(label_building):
    collection = db[label_building]
    all_data = collection.find()
    # filtered_data = [x for x in all_data if x["label_building"] == label_building]
    # print(label_building)
    # docs = database.collection(label_building).stream()
    data = []
    set_of_labels = set()
    for entity in all_data:
        # print(f'{doc.id}')
        list = []
        for key in entity["data"]:
            list.append(entity["data"][key])
        data.append((entity["label_room"], list))
        set_of_labels.add(entity["label_room"])
        # for idUuid in doc.to_dict():
        #     list1 = []
        #     spectrogram = doc.to_dict()[idUuid]
        #     for key in spectrogram:
        #         list1.append(spectrogram[key])
        #     data.append((doc.id, np.asarray(list1)))
        #     set_of_labels.add(doc.id)

    return data, len(set_of_labels)


