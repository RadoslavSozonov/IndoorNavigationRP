import numpy as np

class SignalMock:
    def __init__(self):
        self.x = "data"

    def createMockInput(self, echo_delay):
        SAMPLE_RATE = 44100
        DURATION = 5.0
        NOISE_AMPLITUDE = 0.1
        CHIRP_DURATION = 0.05
        CHIRP_INTERVAL = 0.1

        SHORT_MAX_VALUE = 32767

        ECHO_DELAY = echo_delay  # Delay in seconds
        ECHO_ATTENUATION = 0.4  # Attenuation factor for the echo signal

        audio_length = int(SAMPLE_RATE * DURATION)
        audio = np.zeros(audio_length, dtype=np.int16)

        relative_chirp_duration = int(CHIRP_DURATION * SAMPLE_RATE)  # Adjust the chirp duration as needed
        relative_interval_duration = int(CHIRP_INTERVAL * SAMPLE_RATE)  # Adjust the interval duration as needed

        sin_rate = 15000  # Adjust the frequency of the sine wave as needed

        i = 0
        while i < audio_length:
            for x in range(relative_chirp_duration):
                if i >= audio_length:
                    break
                factor = 0.5 + 0.5 * np.sin(2 * np.pi * x / relative_chirp_duration - 0.5 * np.pi)
                audio[i] = int(np.sin(i * sin_rate) * factor * SHORT_MAX_VALUE)
                audio[i] += int(np.random.uniform(-NOISE_AMPLITUDE, NOISE_AMPLITUDE) * SHORT_MAX_VALUE)
                i += 1

            for x in range(relative_interval_duration):
                if i >= audio_length:
                    break
                audio[i] = int(np.random.uniform(-NOISE_AMPLITUDE * 0.5, NOISE_AMPLITUDE * 0.5) * SHORT_MAX_VALUE)
                i += 1

        # Create an echo signal by delaying the original signal
        echo_delay_samples = int(ECHO_DELAY * SAMPLE_RATE)
        echo_signal = np.concatenate((np.zeros(echo_delay_samples), audio[:-echo_delay_samples]))

        # Add the echo signal to the original signal with attenuation
        audio_with_echo = audio + np.multiply(ECHO_ATTENUATION, echo_signal)

        # Ensure that the audio values are within the valid range
        audio_with_echo = np.clip(audio_with_echo, -SHORT_MAX_VALUE, SHORT_MAX_VALUE)

        # Normalize the audio to the maximum amplitude of a 16-bit signal
        max_amplitude = np.max(np.abs(audio_with_echo))
        normalized_audio = np.array(audio_with_echo / max_amplitude * SHORT_MAX_VALUE, dtype=np.int16)
        return normalized_audio
