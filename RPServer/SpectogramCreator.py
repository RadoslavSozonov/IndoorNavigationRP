import librosa
import matplotlib.pyplot as plt
import numpy as np
import scipy.fft as fft
import scipy.signal as sps

from AudioFilter import AudioFilter

class SpectogramCreator:
    def __init__(self):
        self.audioFilter = AudioFilter()

    def generate_black_white_spectogram(self, audio_data, filename):
        X = librosa.stft(np.array(audio_data))
        Xdb = librosa.amplitude_to_db(abs(X))
        plt.figure(figsize=(14, 5))
        librosa.display.specshow(Xdb, sr=44100, x_axis='time', y_axis='hz')
        plt.colorbar()
        plt.savefig(filename)
        return
    
    def generate_fourier_graph(self, audio_data, filename, smooth):
        N = len(audio_data)
        T = 1.0 / 44100
        yf = fft.fft(audio_data)
        xf = fft.fftfreq(N, T)[: N//2]

        if smooth:
            yf = self.audioFilter.smooth(self.audioFilter.envelope(yf))
        # yf = self.audioFilter.smooth(yf)

        plt.clf()
        plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]))
        plt.grid()
        plt.savefig(filename)
        return yf
    
    def generate_audio_graph(self, audio_data, filename):
        duration = len(audio_data)/44100  # Duration of the audio
        x = np.linspace(0, duration, len(audio_data))
        plt.figure(figsize=(30, 5))
        # plt.plot(x, sound_sample)
        plt.plot(x, audio_data)
        plt.xlabel("duration (s)")
        plt.ylabel("amplitude")
        plt.xlim(0, duration)
        plt.title("Recording")
        plt.savefig(filename)
        return
    
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
    
    def generate_fourier_spectrogram(self, audio_data, filename):
        SHORT_MAX_VALUE = 32767

        # Convert audio data to floating-point values between -1 and 1
        audio_data = audio_data.astype(np.float32) / SHORT_MAX_VALUE

        # Define the window size and overlap
        window_size = 1024
        overlap = window_size // 2

        # Compute the spectrogram using FFT
        frequencies, times, spectrogram, a = plt.specgram(audio_data, NFFT=window_size, Fs=44100, noverlap=overlap)

        spectrogram = np.transpose(spectrogram)

        # Plot the spectrogram
        plt.imshow(np.log10(spectrogram), aspect='auto', origin='lower', cmap='inferno', extent=[times.min(), times.max(), frequencies.min(), frequencies.max()])
        plt.colorbar(label='Magnitude (dB)')
        plt.xlabel('Time (s)')
        plt.ylabel('Frequency (Hz)')
        plt.title('Spectrogram')
        plt.savefig(filename)
        return