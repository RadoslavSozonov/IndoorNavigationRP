import librosa
import matplotlib.pyplot as plt
import numpy as np
import scipy.fft as fft
import scipy.signal as sps

from scipy.signal import spectrogram
from scipy.signal.windows import hann

from AudioFilter import AudioFilter

class SpectogramCreator:
    def __init__(self):
        self.audioFilter = AudioFilter()
        self.yScale = 100
        self.fmin = int(self.yScale / 2 * 0.84)
        self.fmax = int(self.yScale / 2 * 0.94)
        self.hoplength = 156

    def generate_black_white_spectogram(self, audio_data, filename):

        print(len(audio_data))

        X = librosa.stft(np.array(audio_data), n_fft=self.yScale, hop_length=156)
        Xdb = librosa.amplitude_to_db(abs(X))

        print(np.shape(Xdb))

        plt.figure(figsize=(14, 5))
        librosa.display.specshow(Xdb[self.fmin:self.fmax,:], sr=44100)
        plt.colorbar()
        plt.savefig(filename)
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
    
    def generate_spectogram(self, audio_data, filename):
        plt.figure(figsize=(30, 20))
        plt.specgram(audio_data)
        plt.ylabel('Time')
        plt.xlabel('Frequency')
        plt.savefig(filename)
        return
    
    def generate_alternative_spectogram(self, audio_data, filename):
        frame_size = 256  # Number of samples per frame
        hop_length = 128  # Number of samples to shift between frames

        frequencies, times, spectrogram = sps.spectrogram(audio_data, fs=1.0, window='hann',
                                                    nperseg=frame_size, noverlap=frame_size - hop_length)

        # Plot the spectrogram
        plt.figure(figsize=(8, 6))
        plt.pcolormesh(times, frequencies, 10 * np.log10(spectrogram), shading='auto')
        plt.colorbar(label='Power Spectral Density (dB)')
        plt.xlabel('Time')
        plt.ylabel('Frequency')
        plt.title('Spectrogram')
        plt.tight_layout()
        plt.savefig(filename)
        return
    
    def generate_periodogram(self, audio_data, filename):
        frequencies, power_spectrum = sps.periodogram(audio_data)
        plt.figure()
        plt.plot(frequencies, power_spectrum)
        plt.xlabel('Frequency')
        plt.ylabel('Power Spectrum')
        plt.title('Periodogram Analysis')
        plt.grid(True)
        plt.savefig(filename)
        return