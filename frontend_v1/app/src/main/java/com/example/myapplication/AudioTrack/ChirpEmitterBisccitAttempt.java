package com.example.myapplication.AudioTrack;

import android.media.AudioAttributes;
import android.media.AudioFormat;
import android.media.AudioManager;
import android.media.AudioTrack;

public class ChirpEmitterBisccitAttempt {

    private AudioTrack audioTrack;

    private static int sampleRate = 44100;
    private static double interval = 0.1;
    private static double duration = 0.002;

    public ChirpEmitterBisccitAttempt(double frequency, int repeatChirp) {
        int bufferSize = AudioTrack.getMinBufferSize(sampleRate,AudioFormat.CHANNEL_OUT_MONO, AudioFormat.ENCODING_PCM_16BIT);

        AudioTrack audioTrack = new AudioTrack.Builder()
                .setAudioAttributes(new AudioAttributes.Builder()
                        .setUsage(AudioAttributes.USAGE_MEDIA)
                        .setContentType(AudioAttributes.CONTENT_TYPE_UNKNOWN)
                        .build())
                .setAudioFormat(new AudioFormat.Builder()
                        .setEncoding(AudioFormat.ENCODING_PCM_16BIT)
                        .setSampleRate(sampleRate)
                        .setChannelMask(AudioFormat.CHANNEL_OUT_MONO)
                        .build())
                .setBufferSizeInBytes(bufferSize)
                .setTransferMode(AudioTrack.MODE_STREAM)
                .build();

        double break_length = interval - duration;
        double amplitude = 1.0; // between -1.0 and 1.0
        int numSamples = 1 + (int)(duration * sampleRate);

        short[] buffer = new short[numSamples];
        double angularFrequency = 2.0 * Math.PI * frequency;

        for (int i=0; i < numSamples; i++) {
            double time = i / (double) sampleRate;
            double bufferI = amplitude * Math.sin(angularFrequency * time);
            buffer[i] = (short) (bufferI * Short.MAX_VALUE);
        }

        short[] audio = new short[(int) (interval * sampleRate * repeatChirp)];
        int ite = 0;

        while(ite < audio.length) {
            // fill in the chirp
            for(int i = 0; i < buffer.length; i++) {
                audio[ite] = buffer[i];
                ite++;
            }
            // fill in silence
            for(int i = 0; i < (int) (break_length * sampleRate); i++) {
                audio[ite] = (short) 0;
                ite++;
            }
        }

        audioTrack.write(audio, 0, audio.length);
    }

    public void playOnce() {
        this.audioTrack.play();
        this.audioTrack.stop();
        this.audioTrack.reloadStaticData();
    }

    public void destroy() {
        audioTrack.stop();
        audioTrack.release();
    }
}