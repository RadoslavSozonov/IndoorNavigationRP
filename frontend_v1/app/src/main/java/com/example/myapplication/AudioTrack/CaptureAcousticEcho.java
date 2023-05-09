package com.example.myapplication.AudioTrack;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.pm.PackageManager;
import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.MediaRecorder;

import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.example.myapplication.LabelWindow;

import java.util.ArrayList;
import java.util.List;

public class CaptureAcousticEcho implements Runnable {
    private boolean capture = false;
    private AudioRecord audioRecord;
    private boolean stopThread = false;

    public short[] buffer = new short[1];

    public boolean onceStarted = false;


    public CaptureAcousticEcho(AudioRecord audioRecord) {
        this.audioRecord = audioRecord;

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
        while(!this.stopThread){
            this.buffer= new short[(int) (44100*0.1)];// should be 44100*0.1
            int records = 0;
            while (this.capture){
                records = audioRecord.read(this.buffer, 0, buffer.length);
//                System.out.println(records);
            }
            if(onceStarted){
//                System.out.println(records);
            }
        }

    }
}
