import json
import os
import wave
import random

class Database:
    def __init__(self):
        self.jsonfile = 'database\database_layout.json'
        with open(self.jsonfile, 'r') as f:
            self.json = json.load(f)
            f.close()

    def save_image(self, building, room, audio_data):
        if building not in self.json:
            self.json[building] = {}

        filename = "database\\" + str(random.randint(0,99999999)) + ".wav"

        with wave.open(filename, 'w') as file:
            file.setnchannels(1)
            file.setframerate(44100)
            file.setsampwidth(2)
            file.writeframes(audio_data)

        if room not in self.json[building]:
            self.json[building][room] = {}
            self.json[building][room]['data'] = []
            self.json[building][room]['ID'] = random.randint(0,99999999)

        self.json[building][room]['data'].append(filename)

        with open(self.jsonfile, 'w') as f:
            json.dump(self.json, f, indent=4)
            f.close()

    def clear(self):
        with open(self.jsonfile, 'w') as f:
            self.json = {}
            json.dump(self.json, f, indent=4)
            f.close()
        for file in os.listdir('database\\'):
            if file.endswith('.png') or file.endswith('.wav'):
                os.remove('database\\' + file)

    def get_json(self):
        return self.json

    
