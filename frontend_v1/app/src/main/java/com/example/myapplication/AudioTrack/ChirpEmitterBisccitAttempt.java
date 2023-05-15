package com.example.myapplication.AudioTrack;

import android.media.AudioFormat;
import android.media.AudioManager;
import android.media.AudioTrack;

public class ChirpEmitterBisccitAttempt {

    private AudioTrack audioTrack;

    private short[] buffer;

    public ChirpEmitterBisccitAttempt(double frequency) {
        int sampleRate = 44100;
        int bufferSize = AudioTrack.getMinBufferSize(sampleRate,AudioFormat.CHANNEL_OUT_MONO, AudioFormat.ENCODING_PCM_16BIT);

        audioTrack = new AudioTrack(
                AudioManager.STREAM_MUSIC,
                sampleRate,
                AudioFormat.CHANNEL_OUT_MONO,
                AudioFormat.ENCODING_PCM_16BIT,
                bufferSize,
                AudioTrack.MODE_STATIC
        );

        double duration = 0.02;
        double amplitude = 1.0; // between -1.0 and 1.0
        int numSamples = (int)(duration * sampleRate);

        short[] buffer = new short[numSamples];
        double angularFrequency = 2.0 * Math.PI * frequency;

        for (int i=0; i < numSamples; i++) {
            double time = i / (double) sampleRate;
            double bufferI = amplitude * Math.sin(angularFrequency * time);
            buffer[i] = (short) (bufferI * Short.MAX_VALUE);
        }

        audioTrack.write(buffer, 0, buffer.length);
    }

    public void playOnce() {
        audioTrack.play();
        audioTrack.stop();
        audioTrack.reloadStaticData();
    }

    public void destroy() {
        audioTrack.stop();
        audioTrack.release();
    }
}
