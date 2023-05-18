package com.example.myapplication.AudioTrack;

import android.media.AudioAttributes;
import android.media.AudioFormat;
import android.media.AudioManager;
import android.media.AudioTrack;

import com.example.myapplication.Globals;

import java.util.concurrent.BrokenBarrierException;
import java.util.concurrent.CyclicBarrier;

public class ChirpEmitterBisccitAttempt {

    private static int sampleRate = Globals.SAMPLE_RATE;
    private static double interval = Globals.RECORDING_INTERVAL;
    private static double duration = Globals.CHIRP_DURATION;
    public static void playSound(double frequency, int repeatChirp, CyclicBarrier barrier) {

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

        // Rounds up because of floating points
        int numSamples = 1 + (int)(duration * sampleRate);

        short[] buffer = new short[numSamples];
        double angularFrequency = 2.0 * Math.PI * frequency;

        // create chirp buffer
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

        // plays the full audio buffer
        audioTrack.play();
        try {
            barrier.await();
            audioTrack.write(audio, 0, audio.length);
            audioTrack.stop();
            audioTrack.release();
        } catch (BrokenBarrierException e) {
            throw new RuntimeException(e);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }

    }
}
