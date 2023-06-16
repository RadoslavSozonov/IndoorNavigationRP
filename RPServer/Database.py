from genericpath import isfile
import json
import os
import wave
import numpy as np
from PIL import Image

from SpectrogramCreator import SpectrogramCreator

class Database:
    def __init__(self):
        self.sim = SpectrogramCreator()
        self.dbdir = "database\\standard\\"

    def put(self, room, location, audio_data):

        #  make sure the directories exist
        directory = self.dbdir + room

        if not os.path.exists(directory):
            os.makedirs(directory)

        directory += "\\" + location

        if not os.path.exists(directory):
            os.makedirs(directory)

        directory += "\\"
        # save the image in the directory

        ID = len(os.listdir(directory))

        self.sim.generate_black_white_spectogram(audio_data, directory + str(ID))

        return

    def get(self, room, location):
        directory = self.dbdir + room + "\\" + location
        if not os.path.exists(directory):
            return [], [], False
        
        sound_data = []
        labels = []

        for file in os.listdir(directory):
            if os.path.isfile(directory + "\\" + file):
                data = Image.open(directory + "\\" + file)
                data = np.asarray(data)

                sound_data.append(data)
                labels.append(room + ": " + location)

        

        sound_data = np.asarray(sound_data)
        labels = np.asarray(labels)

        return sound_data, labels,  True
    
    def get_all(self):

        data = []
        labels = []
        label_amount = 0

        for room in os.listdir(self.dbdir):
            
            dir = os.path.join(self.dbdir, room)

            for location in os.listdir(dir):
                filedir = os.path.join(dir, location)
                label_amount += 1
                for file in os.listdir(filedir):
                    if os.path.isfile(filedir + "\\" + file):
                        img = Image.open(filedir + "\\" + file)
                        img = np.asarray(img)

                        data.append(img)
                        labels.append(room + ": " + location)


        data = np.asarray(data)
        labels = np.asarray(labels)

        return data, labels, label_amount
    
    def clear(self):
        return

    
