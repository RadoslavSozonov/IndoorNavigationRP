import numpy as np
from PIL import Image
from matplotlib.pyplot import specgram
from scipy.signal import spectrogram
from scipy.signal import windows
import matplotlib.pyplot as plt
import cv2
from DatabaseService import DatabaseService
from datetime import datetime


class SpectogramCreator:

    def __init__(self):
        self.interval_rate = 4410
        self.chirp_error_amount = 2

    def get_offset(self, d1_array):
        spectrum = self.spectrogam_generator(d1_array, 0, "a", "b")
        for i in range(len(spectrum[2])):
            if spectrum[2][i] > 1000:
                # print(i, spectrum[2][i])
                # print(spectrum[2])
                return int(((i)/len(spectrum[2]))*4410)

    def spectrogam_generator(self, d1_array, i, label_building, label_room):
        min_freq = 19600
        max_freq = 20400
        # print(array)
        spectrum, freqs, t, im = specgram(x=d1_array, Fs=44100)
        freq_indices = np.where((freqs >= min_freq) & (freqs <= max_freq))[0]
        spectrum = spectrum[freq_indices, :]
        if i == 5:
            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S').replace(" ", "_").replace(":", "_")
            plt.savefig("photos2/image" + date+"_"+label_building+"_"+label_room + ".png")
        return spectrum

    def createSpectogram(self, label_room, d1_array, label_building, i):
            spectrum = self.spectrogam_generator(d1_array, i, label_building, label_room)
            max_number = np.max(spectrum)
            #print(multiplier)
            # print(spectrum[2])
            # spectrum = (spectrum/max_number)*255
            # firebase.upload_to_real_time_database(label_building, label_room, spectrum)
            #print(spectrum)
            # print(spectrum)
            # f, t, sxx = spectrogram(np.array(array), window=windows.hann(M=256), noverlap=128, fs=20000)
            # print(i, spectrum.shape)
            if i < 20:
                date = datetime.now().strftime('%Y-%m-%d %H:%M:%S').replace(" ", "_").replace(":", "_")
                cv2.imwrite("photos2/"+date+"_"+label_building+"_"+label_room+str(i)+".png", spectrum)

                image = Image.open("photos2/"+date+"_"+label_building+"_"+label_room+str(i)+".png")
                new_image = image.resize((320, 50))
                new_image.save("photos2/"+date+"_"+label_building+"_"+label_room+str(i)+".png")

    def createSpectrogramScipy(self, d1_array):
        # print(d1_array.size)
        min_freq = 19600
        max_freq = 20400
        if d1_array.size != 4410:
            return
        freqs, t, sxx = spectrogram(np.array(self.audioDataBroader(d1_array[133:])), window=windows.hann(M=256), noverlap=128, fs=44100)
        freq_indices = np.where((freqs >= min_freq) & (freqs <= max_freq))[0]
        spectrum = sxx[freq_indices, :]

        max_number = np.max(spectrum)
        spectrum = (spectrum / max_number)
        return spectrum

    def audioDataBroader(self, audioData):
        return audioData
        newData = []
        for number in audioData:
            for y in range(3):
                newData.append(number)
                if len(newData) == 4270:
                    return newData

    def compute_offset(self, np_arr):
        chirp_found = False
        spectgramCreator = SpectogramCreator()
        y = 0
        while True and y < 500:
            # print(i, interval_rate, chirp_sample_offset)
            start_rate = int(y * self.interval_rate)
            sliced = np_arr[start_rate:(int(start_rate + self.interval_rate))]
            # print(sliced)
            for i in range(sliced.size):
                if abs(sliced[i]) > 10000:
                    print(i - 50)
                    return i - 50
            y += 1

        if chirp_found == False:
            return "Failure"




