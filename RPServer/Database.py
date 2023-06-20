from genericpath import isfile
import json
import os
import wave
import numpy as np
from PIL import Image
import globals

from SpectrogramCreator import SpectrogramCreator

class Database:
    def __init__(self):
        self.sim = SpectrogramCreator()
        self.dbdir = "database\\"

    def load_image(self, filename):
        data = Image.open(filename)
        data = np.asarray(data)
        return data

    def put(self, room, location, audio_data):

        for type in globals.SPECTROGRAM_TYPES:
            #  make sure the directories exist
            directory = self.dbdir + type + "\\" + room

            if not os.path.exists(directory):
                os.makedirs(directory)

            directory += "\\" + location

            if not os.path.exists(directory):
                os.makedirs(directory)

            directory += "\\"
            # save the image in the directory

            ID = len(os.listdir(directory))

            self.create_spectrogram(audio_data, directory + str(ID), type)

        return
    
    def create_spectrogram(self, audio_data, filename, type):
        if type == "standard":
            self.sim.generate_spectogram(audio_data, filename)
        elif type == "chroma":
            self.sim.generate_chroma_spectrogram(audio_data, filename)
        elif type == "mfccs":
            self.sim.generate_mfccs_spectrogram(audio_data, filename)
        elif type == "mel":
            self.sim.generate_mel_spectrogram(audio_data, filename)
        elif type == "db_standard":
            self.sim.generate_db_spectrogram(audio_data, filename)

    def get(self, room, location):
        directory = self.dbdir + room + "\\" + location
        if not os.path.exists(directory):
            return [], [], False
        
        sound_data = []
        labels = []

        for file in os.listdir(directory):
            if os.path.isfile(directory + "\\" + file):
                data = self.load_image(directory + "\\" + file)

                sound_data.append(data)
                labels.append(room + ": " + location)

        sound_data = np.asarray(sound_data)
        labels = np.asarray(labels)

        return sound_data, labels,  True
    
    def get_all(self, type):

        data = []
        labels = []
        label_amount = 0

        directory = self.dbdir + type + "\\"

        for room in os.listdir(directory):
            
            
            dir = os.path.join(directory, room)

            if not os.path.isfile(dir):

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

    
