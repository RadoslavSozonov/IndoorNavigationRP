import numpy as np
from PIL import Image
from matplotlib.pyplot import specgram
from scipy.signal import spectrogram
from scipy.signal import windows
import matplotlib.pyplot as plt
import cv2
import firebaseConfig as firebase

class SpectogramCreator:
    def __init__(self):
        self.x = "data"

    def createSpectogram(self, label_room, d1_arrays, label_building, i):

        for array in d1_arrays:
            spectrum = self.createSpectogramData(array)

            # print("SHAPE: " + str(spectrum.shape))

            firebase.upload_to_real_time_database(label_building, label_room, spectrum)

            filename = "saved\\images\\spectrum_building_" + label_building + "_room_" + label_room + "_" +str(i)+".png"

            cv2.imwrite(filename, spectrum)
            # image = cv2.read("photos2/image"+str(i)+".png")

            image = Image.open(filename)
            new_image = image.resize((320, 50))
            new_image.save(filename)

    def createSpectogramData(self, d1_array):
        min_freq = 19600
        max_freq = 20400

        spectrum, freqs, t, im = specgram(x=d1_array[110:], Fs=44100)
        freq_indices = np.where((freqs >= min_freq) & (freqs <= max_freq))[0]
        spectrum = spectrum[freq_indices, :]
        max_number = np.max(spectrum)

        spectrum = (spectrum/max_number)*255
        return spectrum