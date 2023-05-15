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

    public CaptureAcousticEcho(AudioRecord audioRecord) {
        this.audioRecord = audioRecord;

    }

    public void stopCapture(){
        this.capture = false;
    }

    public void startCapture() {
        this.capture = true;
    }

    public void stopThread(){
        this.stopThread = true;
    }


    @Override
    public void run() {
        this.buffer= new short[(int) (44100*0.1)];// should be 44100*0.1
        while(!this.stopThread){
            while (this.capture){
                audioRecord.read(this.buffer, 0, buffer.length);
            }
        }
    }
}
