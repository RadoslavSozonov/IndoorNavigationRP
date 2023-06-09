import json
import os
import wave
import random
import numpy as np

class Database:
    def __init__(self):
        self.jsonfile = 'database\database_layout.json'
        with open(self.jsonfile, 'r') as f:
            self.json = json.load(f)
            f.close()

    def save_image(self, building, room, audio_data):
        if building not in self.json['Buildings']:
            self.json['Buildings'][building] = {}

        filename = "database\\" + str(random.randint(0,99999999)) + ".npy"

        float_array = np.array(audio_data, dtype=np.float32)
        np.save(filename, float_array)

        if room not in self.json['Buildings'][building]:
            self.json['Buildings'][building][room] = {}
            self.json['Buildings'][building][room]['data'] = []
            self.json['Buildings'][building][room]['ID'] = self.json['Config']['curIndex']
            self.json['Config']['curIndex'] += 1

        self.json['Buildings'][building][room]['data'].append(filename)

        with open(self.jsonfile, 'w') as f:
            json.dump(self.json, f, indent=4)
            f.close()

    def clear(self):
        with open(self.jsonfile, 'w') as f:
            self.json = {"Config" : {"curIndex" : 0}, "Buildings" : {}}
            json.dump(self.json, f, indent=4)
            f.close()
        for file in os.listdir('database\\'):
            if file.endswith('.png') or file.endswith('.npy'):
                os.remove('database\\' + file)

    def get_json(self):
        # with open(self.jsonfile, 'w') as f:
        #     self.json = json.load(f)
        #     f.close()
        return self.json

    
