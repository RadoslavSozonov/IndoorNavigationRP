package com.example.myapplication.AudioTrack;

import android.media.AudioFormat;
import android.media.AudioManager;
import android.media.AudioTrack;

// ChatGPT code
public class ChirpEmitterGPT {
    private static final int SAMPLE_RATE = 44100; // Sample rate in Hz
    private static final int DURATION_MS = 500; // Chirp duration in milliseconds

    public static void emitChirp(float frequency) {
        int numSamples = (int) ((float) SAMPLE_RATE * DURATION_MS / 1000);
        short[] buffer = new short[numSamples];

        // Generate the chirp waveform
        double frequencyStart = frequency; // Chirp starting frequency in Hz
        double frequencyEnd = frequency; // Chirp ending frequency in Hz
        double phase = 0;
        double phaseIncrement = (frequencyEnd - frequencyStart) * 2 * Math.PI / SAMPLE_RATE;

        for (int i = 0; i < numSamples; i++) {
            buffer[i] = (short) (Math.sin(phase) * Short.MAX_VALUE);
            phase += phaseIncrement;
        }

        // Configure the audio track
        int bufferSize = AudioTrack.getMinBufferSize(SAMPLE_RATE, AudioFormat.CHANNEL_OUT_MONO, AudioFormat.ENCODING_PCM_16BIT);
        AudioTrack audioTrack = new AudioTrack(AudioManager.STREAM_MUSIC, SAMPLE_RATE, AudioFormat.CHANNEL_OUT_MONO,
                AudioFormat.ENCODING_PCM_16BIT, bufferSize, AudioTrack.MODE_STREAM);

        // Start playback
        audioTrack.play();

        // Write the chirp data to the audio track
        audioTrack.write(shortArrayToByteArray(buffer), 0, buffer.length);

        // Release resources
        audioTrack.stop();
        audioTrack.release();
    }

    private static byte[] shortArrayToByteArray(short[] array) {
        byte[] byteArray = new byte[array.length * 2];
        for (int i = 0; i < array.length; i++) {
            byteArray[i * 2] = (byte) (array[i] & 0xff);
            byteArray[i * 2 + 1] = (byte) ((array[i] >> 8) & 0xff);
        }
        return byteArray;
    }
}
