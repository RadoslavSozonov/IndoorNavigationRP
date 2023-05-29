package com.example.myapplication.AudioTrack;

import android.media.AudioAttributes;
import android.media.AudioFormat;
import android.media.AudioManager;
import android.media.AudioTrack;

public class ChirpEmitterBisccitAttempt {

    private AudioTrack audioTrack;

    private short[] buffer;

    private int repeatChirp;

    public static void playSound(double frequency, int repeatChirp) {
        int sampleRate = 44100;
        int bufferSize = AudioTrack.getMinBufferSize(sampleRate,AudioFormat.CHANNEL_OUT_MONO, AudioFormat.ENCODING_PCM_16BIT);

        double sinRate = frequency * Math.PI / (0.5 * sampleRate);

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


        double duration = 1;
        double chirpDuration = 0.05;
        double chirpInterval = 0.1;

        int relativeChirpDuration = (int)(chirpDuration * sampleRate);
        int relativeIntervalDuration = (int)(chirpInterval * sampleRate);

        short[] audio = new short[(int)(sampleRate * duration)];

        for (int i=0;i<audio.length;){

            for (int x=0;x<relativeChirpDuration && i<audio.length;x++, i++) {
                double factor = 1;//0.5 + 0.5 * Math.sin(2 * Math.PI * x / relativeChirpDuration - 0.5 * Math.PI);
                audio[i] = (short)(Short.MAX_VALUE * Math.sin(i * sinRate) * factor);
            }

            for (int x=0;x<relativeIntervalDuration && i<audio.length;x++, i++) {
                audio[i] = 0;
            }
        }

        audioTrack.play();
        audioTrack.write(audio, 0, audio.length);
        audioTrack.stop();
        audioTrack.release();
    }
}