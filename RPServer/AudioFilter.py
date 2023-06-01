import scipy.signal as sps

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
