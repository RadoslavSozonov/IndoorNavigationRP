import librosa
import matplotlib.pyplot as plt
import numpy as np
import scipy.fft as fft
import scipy.signal as sps
import cv2
import time

from scipy.signal import spectrogram
from scipy.signal.windows import hann

from AudioFilter import AudioFilter

class SpectrogramCreator:
    def __init__(self):
        self.audioFilter = AudioFilter()
        self.yScale = 100
        self.fmin = int(self.yScale / 2 * 0.899)
        self.fmax = int(self.yScale / 2 * 0.999)
        self.hoplength = 156

    def generate_spectogram(self, audio_data, filename):
        X = librosa.stft(np.array(audio_data), n_fft=self.yScale, hop_length=156)

        plt.clf()
        librosa.display.specshow(X[self.fmin:self.fmax,:], sr=44100)
        plt.axis('off')
        plt.savefig(filename, bbox_inches="tight", pad_inches=0)

        self.convert_spectrogram(filename)
        
        return
    
    def generate_mfccs_spectrogram(self, audio_data, filename):
        plt.clf()
        mfccs = librosa.feature.mfcc(y=audio_data, sr=44100, n_mfcc=10, fmin=19500, fmax=20500, hop_length=100)
        librosa.display.specshow(mfccs, sr=44100)
        plt.axis('off')
        plt.savefig(filename, bbox_inches="tight", pad_inches=0)
        self.convert_spectrogram(filename)
        return
    
    def generate_mel_spectrogram(self, audio_data, filename):
        plt.clf()
        mel = librosa.feature.melspectrogram(y=audio_data, sr=44100, fmin=19500, n_mels=10, fmax=20500, hop_length=156)
        librosa.display.specshow(mel, sr=44100)
        plt.axis('off')
        plt.savefig(filename, bbox_inches="tight", pad_inches=0)
        self.convert_spectrogram(filename)
        return
    
    def generate_db_spectrogram(self, audio_data, filename):
        plt.clf()
        X = librosa.stft(np.array(audio_data), n_fft=self.yScale, hop_length=156)
        Xdb = librosa.amplitude_to_db(abs(X))
        librosa.display.specshow(Xdb[self.fmin:self.fmax,:], sr=44100)
        plt.axis('off')
        plt.savefig(filename, bbox_inches="tight", pad_inches=0)
        self.convert_spectrogram(filename)
        return
    
    def generate_chroma_spectrogram(self, audio_data, filename):
        plt.clf()
        chromagram = librosa.feature.chroma_stft(y=audio_data, sr=44100, hop_length=128)
        librosa.display.specshow(chromagram, x_axis='time', y_axis='chroma',  cmap='coolwarm')
        plt.savefig(filename, bbox_inches="tight", pad_inches=0)
        self.convert_spectrogram(filename)
        return

    def convert_spectrogram(self, filename):
        # code from davis
        time.sleep(0.1)

        rgb = cv2.imread(filename + '.png')

        rgb = cv2.resize(rgb, (32, 5))
        not_rgb = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
        scale = 255/np.max(not_rgb)
        not_rgb = (not_rgb * scale).astype(np.uint8)
        cv2.imwrite(filename + '.png', not_rgb)
        return