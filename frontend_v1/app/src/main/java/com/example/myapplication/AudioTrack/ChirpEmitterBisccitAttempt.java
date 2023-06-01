package com.example.myapplication.AudioTrack;

import android.media.AudioAttributes;
import android.media.AudioFormat;
import android.media.AudioManager;
import android.media.AudioTrack;
import android.media.audiofx.LoudnessEnhancer;

import com.example.myapplication.Globals;

public class ChirpEmitterBisccitAttempt {

    private AudioTrack audioTrack;

    private short[] buffer;

    private int repeatChirp;

    public static void playSound(int repeatChirp) {
        int bufferSize = AudioTrack.getMinBufferSize(Globals.SAMPLE_RATE,AudioFormat.CHANNEL_OUT_MONO, AudioFormat.ENCODING_PCM_16BIT);

        double sinRate = Globals.CHIRP_FREQUENCY * Math.PI / (0.5 * Globals.SAMPLE_RATE);

        AudioTrack audioTrack = new AudioTrack.Builder()
                .setAudioAttributes(new AudioAttributes.Builder()
                        .setUsage(AudioAttributes.USAGE_MEDIA)
                        .setContentType(AudioAttributes.CONTENT_TYPE_UNKNOWN)
                        .build())
                .setAudioFormat(new AudioFormat.Builder()
                        .setEncoding(AudioFormat.ENCODING_PCM_16BIT)
                        .setSampleRate(Globals.SAMPLE_RATE)
                        .setChannelMask(AudioFormat.CHANNEL_OUT_MONO)
                        .build())
                .setBufferSizeInBytes(bufferSize)
                .setTransferMode(AudioTrack.MODE_STREAM)
                .build();

        int relativeChirpDuration = (int)(Globals.CHIRP_DURATION * Globals.SAMPLE_RATE);
        int relativeIntervalDuration = (int)(Globals.CHIRP_INTERVAL * Globals.SAMPLE_RATE);

        short[] audio = new short[(int)(Globals.SAMPLE_RATE * Globals.DURATION)];

        for (int i=0;i<audio.length;){

            for (int x=0;x<relativeChirpDuration && i<audio.length;x++, i++) {
                double factor = 0.5 + 0.5 * Math.sin(2 * Math.PI * x / relativeChirpDuration - 0.5 * Math.PI);
                audio[i] = (short)(Short.MAX_VALUE * Math.sin(i * sinRate) * factor);
            }

            for (int x=0;x<relativeIntervalDuration && i<audio.length;x++, i++) {
                audio[i] = 0;
            }
        }

//        LoudnessEnhancer enhancer = new LoudnessEnhancer(audioTrack.getAudioSessionId());
//
//        enhancer.setTargetGain(5000);
//        enhancer.setEnabled(true);

        audioTrack.play();
        audioTrack.write(audio, 0, audio.length);
        audioTrack.stop();
        audioTrack.release();
    }
}