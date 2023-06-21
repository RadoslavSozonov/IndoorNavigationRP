import os
from scipy.io import wavfile
import numpy as np
from SpectogramCreator import SpectogramCreator


class Converter:
    def __init__(self):
        self.interval_rate = 4410
        self.chirp_error_amount = 2

    def convert_wav_to_spectrograms(self):
        for place in os.listdir("wav_files/"):
            if not place.__contains__("EWI"):
                continue
            spectrogramCreator = SpectogramCreator()
            samplerate, wav_array = wavfile.read('wav_files/' + place)
            np_arr = np.asarray(wav_array, dtype=np.int16)
            chirp_sample_offset = spectrogramCreator.compute_offset(np_arr)
            name = 'text_files_spectrograms/' + place.split(".")[0].lower() + ".txt"
            mode = 'w'
            data = ""

            for i in range(100):
                start_rate = int((i + 2) * self.interval_rate + chirp_sample_offset)
                sliced = np_arr[start_rate:(int(start_rate + self.interval_rate))]
                spectrogram = spectrogramCreator.createSpectrogramScipy(sliced)
                # print(sliced)
                for row in spectrogram:
                    for element in row:
                        data += f"{element}\n"
                    data += f"A\n"
                data += f"B\n"

            Converter().to_txt_file(name, mode, data)

    def convert_wav_to_text_file(self):
        for place in os.listdir("wav_files/"):
            if not place.__contains__("EWI"):
                continue
            samplerate, wav_array = wavfile.read('wav_files/' + place)
            name = 'text_files/' + place.split(".")[0].lower() + ".txt"
            mode = 'w'
            data = ""
            for line in wav_array[:100 * 4410]:
                data += f"{line}\n"
            self.to_txt_file(name, mode, data)

    def save_spectrogram_to_txt(self, spectrogram, name):
        name = 'text_files/' + name + ".txt"
        mode = 'a'
        data = ""

        for row in spectrogram:
            for element in row:
                data += f"{element}\n"
            data += f"A\n"
        data += f"B\n"

        self.to_txt_file(name, mode, data)

    def json_to_audio_data_converter(self, dictionary):
        i = 0
        for key in dictionary:
            i += 1
            dictionary[key] = [int(i) for i in dictionary[key].strip('][').split(', ')]
        np_arr = np.asarray([])
        for key in dictionary:
            big_array = dictionary[key][int(0):]
            np_arr = np.asarray(big_array, dtype=np.int16)

        return np_arr

    def to_txt_file(self, name, mode, data):
        with open(name, mode) as f:
            f.write(data)
            f.close()
