import scipy.signal as sps
import numpy as np

class AudioFilter:
    def __init__(self):
        self.x = "data"

    def apply_high_pass_filter(self, audio_data, cutoff_frequency):
        # CUTOFF LOWER FREQUENCIES
        sampling_rate = 44100  # Specify the sampling rate in Hz

        # Convert the cutoff frequency to a normalized value
        nyquist_frequency = 0.5 * sampling_rate
        normalized_cutoff_frequency = cutoff_frequency / nyquist_frequency

        # Design the high-pass filter
        b, a = sps.butter(4, normalized_cutoff_frequency, btype='high', analog=False, output='ba')

        # Apply the high-pass filter to the input signal
        return sps.lfilter(b, a, audio_data)
    
    def apply_low_pass_filter(self, audio_data, cutoff_frequency):
        # CUTOFF LOWER FREQUENCIES
        sampling_rate = 44100  # Specify the sampling rate in Hz

        # Convert the cutoff frequency to a normalized value
        nyquist_frequency = 0.5 * sampling_rate
        normalized_cutoff_frequency = cutoff_frequency / nyquist_frequency

        # Design the high-pass filter
        b, a = sps.butter(4, normalized_cutoff_frequency, btype='low', analog=False, output='ba')

        # Apply the high-pass filter to the input signal
        return sps.lfilter(b, a, audio_data)
    
    def apply_filter(self, audio_data):
        b, a = sps.butter(1, 0.5)
        filtered = sps.filtfilt(b, a, audio_data)
        return filtered
    
    def envelope(self, audio_data):
        sample_rate = 44100
        SHORT_MAX_VALUE = 32767

        # Convert audio data to floating-point values between -1 and 1
        audio_data = audio_data.astype(np.float32) / SHORT_MAX_VALUE

        # Rectify the audio signal
        rectified_audio = np.abs(audio_data)

        # Define the parameters for the low-pass filter
        cutoff_freq = 1000  # Adjust the cutoff frequency as needed
        filter_order = 4    # Adjust the filter order as needed

        # Create the low-pass filter
        nyquist_freq = 0.5 * sample_rate
        normalized_cutoff = cutoff_freq / nyquist_freq
        b, a = sps.butter(filter_order, normalized_cutoff, btype='low', analog=False)

        # Apply the low-pass filter
        filtered_audio = sps.filtfilt(b, a, rectified_audio)

        # Scale the filtered audio back to the original range
        envelope = filtered_audio * SHORT_MAX_VALUE

        # Convert the envelope back to the original data type
        envelope = envelope.astype(audio_data.dtype)

        # Save the envelope to a new file
        return envelope

    def smooth(self, audio_data):
        N = 250
        return np.convolve(audio_data, np.ones(N) / N, mode='valid')
        # window = 1000
        # res = []
        # for i in range(len(audio_data) - window + 1):
        #     res.append(np.mean(audio_data[i:i + window]))
        # return res
