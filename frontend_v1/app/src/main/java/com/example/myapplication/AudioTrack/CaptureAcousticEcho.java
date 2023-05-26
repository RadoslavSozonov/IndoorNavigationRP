package com.example.myapplication.AudioTrack;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.pm.PackageManager;
import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.MediaRecorder;
import android.util.Log;

import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.example.myapplication.LabelWindow;
import com.example.myapplication.Util;

import java.util.ArrayList;
import java.util.List;

public class CaptureAcousticEcho implements Runnable {

    private int repeatChirp;
    private boolean capture = false;
    private AudioRecord audioRecord;
    private boolean stopThread = false;

    public float[] buffer = new float[1];

    public boolean onceStarted = false;

    private int bufferSize;


    public CaptureAcousticEcho(AudioRecord audioRecord, int repeatChirp) {
        this.audioRecord = audioRecord;
        this.repeatChirp = repeatChirp;
        int bufferSize = (int) (44100 * 0.1 * repeatChirp);
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
