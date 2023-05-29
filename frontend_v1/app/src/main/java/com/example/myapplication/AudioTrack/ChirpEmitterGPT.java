package com.example.myapplication.AudioTrack;

import android.media.AudioFormat;
import android.media.AudioManager;
import android.media.AudioTrack;

// ChatGPT code
public class ChirpEmitterGPT {
    private static final int SAMPLE_RATE = 44100; // Sample rate in Hz
    private static final int DURATION_MS = 2000; // Chirp duration in milliseconds

    public static void playSound(float frequency, int repeatChirp) {

        double duration = DURATION_MS / 1000;

        int numSamples = (int) ((float) SAMPLE_RATE * duration);
        short[] buffer = new short[numSamples];

        double chirpDuration = 0.1;  // Duration of each individual chirp in seconds
        double interval = 0.05;  // Interval between chirps in seconds

        double intervalSamples = SAMPLE_RATE * interval;
        double chirpSamples = SAMPLE_RATE * chirpDuration;

        for (int i = 0; i < numSamples; i++) {
            double time = (double) i / SAMPLE_RATE;
            double value = 0.0;

            if (time % chirpDuration <= chirpDuration / 2) {
                value = Math.sin(2 * Math.PI * frequency * time * (1 + time));
            }

            buffer[i] = (short) (Short.MAX_VALUE * value);
        }


        AudioTrack audioTrack = new AudioTrack(AudioManager.STREAM_MUSIC, SAMPLE_RATE, AudioFormat.CHANNEL_OUT_MONO,
                AudioFormat.ENCODING_PCM_16BIT, numSamples, AudioTrack.MODE_STREAM);

        // Start playback
        audioTrack.play();
        // Write the chirp data to the audio track
        audioTrack.write(buffer, 0, buffer.length);
        // Release resources
        audioTrack.stop();
        audioTrack.release();
    }
}
