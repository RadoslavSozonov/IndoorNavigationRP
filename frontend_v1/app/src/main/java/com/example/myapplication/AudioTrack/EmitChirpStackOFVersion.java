package com.example.myapplication.AudioTrack;

import android.media.AudioAttributes;
import android.media.AudioFormat;
import android.media.AudioTrack;

public class EmitChirpStackOFVersion {
    private float duration;
    private int freq1;
    private int freq2;


    private AudioTrack audioTrack = null;

    // I (roald) decided to write some comments to get some understanding
    public EmitChirpStackOFVersion(int freq1, int freq2, float duration){
        this.duration=duration;
        this.freq1=freq1;
        this.freq2=freq2;

        int sampleRate=44100;
        int numSample= (int) (this.duration*sampleRate);
        double sample[]=new double[numSample];
        byte[] generatedSnd= new byte[2*numSample];
        double instfreq=0, numerator;
//        float c = (this.freq2 - this.freq1)/this.duration;

        System.out.println(numSample);

        for (int i=0;i<numSample; i++) {
            numerator=(double)(i)/(double)numSample; // t (between 0 and 1)

            instfreq=freq1+(numerator*(this.freq2-this.freq1)); // results in a value between freq1 and freq2

            sample[i]=Math.sin(2*Math.PI*i/(sampleRate/instfreq)); // not sure what this is supposed to mean

//            sample[i] = Math.sin(2*Math.PI*(freq1 + ((freq2-freq1)*numerator)/duration));
//            System.out.println(sample[i]);
        }

        int idx = 0;
        for (final double dVal : sample) {
            // scale to maximum amplitude
            final short val = (short) ((dVal * 32767)); // max positive sample for signed 16 bit integers is 32767
            // in 16 bit wave PCM, first byte is the low order byte (pcm: pulse control modulation)
            generatedSnd[idx++] = (byte) (val & 0x00ff);
            generatedSnd[idx++] = (byte) ((val & 0xff00) >>> 8);
        }

        try {
            AudioAttributes audioAttributes = new AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_ALARM)
                    .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                    .build();
            AudioFormat audioFormat = new AudioFormat.Builder()
                    .setSampleRate(sampleRate)
                    .setChannelMask(AudioFormat.CHANNEL_OUT_MONO)
                    .setEncoding(AudioFormat.ENCODING_PCM_16BIT)
                    .build();

            this.audioTrack = new AudioTrack(
                    audioAttributes,
                    audioFormat,
                    generatedSnd.length,
                    AudioTrack.MODE_STATIC,
                    1
            );
            this.audioTrack.write(generatedSnd, 0, generatedSnd.length);
        } catch (Exception e){
            System.out.println(e.toString());
        }
    }

//    public void playSoundMultipleTimes(int times){
//        try {
//            System.out.println("Start");
//            for(int i = 0; i < times; i++){
//                playSoundOnce();
//            }
//
//            System.out.println("Sound played Git");
//        } catch (Exception e){
//            System.out.println(e.toString());
//        }
//    }

    public void playSoundOnce(){

        this.audioTrack.play();
        this.audioTrack.stop();
        this.audioTrack.reloadStaticData();
    }
}
