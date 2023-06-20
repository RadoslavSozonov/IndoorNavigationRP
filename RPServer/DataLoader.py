import os
import random
import numpy as np
from scipy.io import wavfile
from sklearn.model_selection import train_test_split
from Converter import Converter
from DatabaseService import DatabaseService
from SpectogramCreator import SpectogramCreator


class DataLoader:

    def __init__(self):
        self.interval_rate = 4410
        self.chirp_error_amount = 2

    def load_data_in_db(self, data_building):
        spectgramCreator = SpectogramCreator()

        for place in os.listdir("wav_files/"):
            if not place.__contains__(data_building):
                continue
            samplerate, wav_array = wavfile.read('wav_files/' + place)
            np_arr = np.asarray(wav_array[int(4 * self.interval_rate):], dtype=np.int16)
            chirp_sample_offset = SpectogramCreator.compute_offset(np_arr)

            letter = place.split("_")[-1].split(".")[0]

            for i in range(int(np_arr.size / self.interval_rate) - self.chirp_error_amount):
                start_rate = int((i + 1) * self.interval_rate + chirp_sample_offset)
                sliced = np_arr[start_rate:(int(start_rate + self.interval_rate))]
                spectrum = spectgramCreator.createSpectrogramScipy(sliced)
                DatabaseService().upload_to_real_time_database(data_building, letter, spectrum)
                Converter().save_spectrogram_to_txt(spectrum, place.split(".")[0])

    def load_model_data_from_db(self, building, train_size):
        data, labelsN = DatabaseService().getData(building)
        labels = [unit[0] for unit in data]
        map_label_encoding = {}
        value = 0
        for label in labels:
            if label not in map_label_encoding:
                map_label_encoding[label] = value
                value += 1
        spectrograms = [unit[1] for unit in data]
        encoded_labels = [map_label_encoding[label] for label in labels]
        shuffled_list = self.shuffle(spectrograms, encoded_labels)
        train_x = np.array([x[0] for x in shuffled_list])
        train_y = np.array([x[1] for x in shuffled_list])
        X_train, X_test, y_train, y_test = train_test_split(train_x, train_y, train_size=train_size, shuffle=True,
                                                            random_state=1)
        data_info = {
            "X_train": X_train,
            "X_test": X_test,
            "y_train": y_train,
            "y_test": y_test,
            "labelsN": labelsN,
            "labels": map_label_encoding.keys()
        }
        return data_info

    def shuffle(self, spectrograms, encoded_labels):

        to_shuffle = []
        for i in range(len(encoded_labels)):
            to_shuffle.append((spectrograms[i], encoded_labels[i]))

        shuffled_list = []
        for i in range(10000):
            shuffled_list = random.sample(to_shuffle, k=len(to_shuffle))

        return shuffled_list