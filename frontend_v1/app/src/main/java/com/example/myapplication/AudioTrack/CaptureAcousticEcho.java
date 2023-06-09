package com.example.myapplication.AudioTrack;

import android.media.AudioRecord;
import android.util.Log;

import com.example.myapplication.Globals;

public class CaptureAcousticEcho implements Runnable {

    private boolean capture = false;
    private AudioRecord audioRecord;
    private boolean stopThread = false;

    public float[] buffer;

    public boolean onceStarted = false;

    private int bufferSize;


    public CaptureAcousticEcho(AudioRecord audioRecord, double duration) {
        this.audioRecord = audioRecord;
        int bufferSize = (int) (44100 * duration);
        this.bufferSize = bufferSize;
        this.buffer= new float[bufferSize];// should be 44100*0.1
    }

    public void stopCapture(){
        this.capture = false;
//        audioRecord.stop();
//        audioRecord.release();
    }

    public void startCapture() {
        this.capture = true;
        onceStarted = true;
    }

    public void stopThread(){
        this.stopThread = true;
//        audioRecord.stop();
//        audioRecord.release();
    }


    @Override
    public void run() {
        long start = System.currentTimeMillis();
        audioRecord.startRecording();
        int res = audioRecord.read(this.buffer, 0, bufferSize, AudioRecord.READ_BLOCKING);
        Log.d("record result", "" +  res);
        Log.i("recording duration", "" + (System.currentTimeMillis()-start));
        //Log.i("BUFFER", "" + Util.printArray(buffer, 1000, 1100));

    }
}
