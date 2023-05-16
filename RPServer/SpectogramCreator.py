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
            min_freq = 19600
            max_freq = 20400


            # fig, ax = plt.subplots()
            spectrum, freqs, t, im = specgram(x=array[110:], Fs=44100)
            freq_indices = np.where((freqs >= min_freq) & (freqs <= max_freq))[0]
            spectrum = spectrum[freq_indices, :]
            max_number = np.max(spectrum)

            #print(multiplier)
            #print(spectrum)
            spectrum = (spectrum/max_number)*255
            firebase.upload_to_real_time_database(label_building, label_room, spectrum)
            #print(spectrum)
            # print(spectrum)
            # f, t, sxx = spectrogram(np.array(array), window=windows.hann(M=256), noverlap=128, fs=20000)
            # print(i, spectrum.shape)

            cv2.imwrite("photos2/image"+str(i)+".png", spectrum)
            # image = cv2.read("photos2/image"+str(i)+".png")

            image = Image.open("photos2/image"+str(i)+".png")
            new_image = image.resize((320, 50))
            new_image.save("photos2/image"+str(i)+".png")




