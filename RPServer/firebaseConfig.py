# import firebase_admin
# from firebase_admin import credentials, firestore
from pymongo import MongoClient
import uuid
import numpy as np


# cred = credentials.Certificate("key.json")
# app = firebase_admin.initialize_app(cred)
# database = firestore.client()

client = MongoClient('localhost', 27017)
db = client["RPServer"]

class Firebase():
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        self.firebaseData = []
        self.labels = 0

    def upload_to_real_time_database(self, label_building, label_room, spectgram):
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

    def getData(self, label_building):
        if self.labels == 0:
            self.firebaseData, self.labels = self.get_from_real_time_database(label_building)
            print("Data loaded", self.labels)
        return self.firebaseData, self.labels

    def get_from_real_time_database(self, label_building):
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
            # if entity["label_room"] == "C" or entity["label_room"] == "D":
            data.append((entity["label_room"], list))
            set_of_labels.add(entity["label_room"])

        return data, len(set_of_labels)


