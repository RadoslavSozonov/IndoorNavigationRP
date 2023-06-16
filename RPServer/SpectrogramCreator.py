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

    def generate_black_white_spectogram(self, audio_data, filename):
        X = librosa.stft(np.array(audio_data), n_fft=self.yScale, hop_length=156)
        Xdb = librosa.amplitude_to_db(abs(X))

        plt.clf()
        librosa.display.specshow(Xdb[self.fmin:self.fmax,:], sr=44100)
        plt.axis('off')
        plt.savefig(filename, bbox_inches="tight", pad_inches=0)

# code from davis
        time.sleep(0.1)

        rgb = cv2.imread(filename + '.png')

        rgb = cv2.resize(rgb, (32, 5))
        not_rgb = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
        scale = 255/np.max(not_rgb)
        not_rgb = (not_rgb * scale).astype(np.uint8)
        cv2.imwrite(filename + '.png', not_rgb)
        
        return
    
    def generate_spect(self, audio_data, filename):
        f, t, Sxx = spectrogram(audio_data, 44100, window=hann(256, sym=False))
        high_frequency_indices = np.where((f > 19500) & (f < 20500))
        f = f[high_frequency_indices]
        Sxx = Sxx[high_frequency_indices]

        plt.clf()
        plt.pcolormesh(t, f, Sxx, shading='nearest')
        plt.axis('off')
        plt.savefig(filename, bbox_inches="tight", pad_inches=0)

        

        
    
    def generate_mfccs_spectrogram(self, audio_data, filename):
        plt.clf()
        mfccs = librosa.feature.mfcc(y=audio_data, sr=44100,  hop_length=512)
        librosa.display.specshow(mfccs, sr=44100, x_axis='time', y_axis='hz')
        plt.colorbar()
        plt.savefig(filename)
        return
    
    def generate_chroma_spectrogram(self, audio_data, filename):
        plt.clf()
        chromagram = librosa.feature.chroma_stft(y=audio_data, sr=44100, hop_length=128)
        librosa.display.specshow(chromagram, x_axis='time', y_axis='chroma',  cmap='coolwarm')
        plt.savefig(filename)