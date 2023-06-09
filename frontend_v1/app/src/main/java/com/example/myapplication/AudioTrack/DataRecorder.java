package com.example.myapplication.AudioTrack;

import android.Manifest;
import android.app.Activity;
import android.content.pm.PackageManager;
import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.MediaRecorder;
import android.util.Log;
import android.widget.TextView;

import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.example.myapplication.Globals;
import com.example.myapplication.R;
import com.example.myapplication.RequestCallbacks.RecordingCallback;
import com.example.myapplication.Util;

import org.json.JSONException;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Timer;
import java.util.TimerTask;
import java.util.stream.Collectors;

public class DataRecorder {

    private Activity activity;

    private RecordingCallback callback;

    private double duration;

    public DataRecorder(double duration, Activity activity, RecordingCallback callback) {
        this.activity = activity;
        this.callback = callback;
        this.duration = duration;
    }

    public void recordData() {
        //ChirpEmitterBisccitAttempt chirpEmitter = new ChirpEmitterBisccitAttempt(CHIRP_FREQUENCY, chirpRepeat);

        AudioRecord audioRecord = createAudioRecord();
        System.out.println(audioRecord.getState());
        CaptureAcousticEcho captureAcousticEcho = new CaptureAcousticEcho(audioRecord ,duration);
//                    Thread threadCapture = new Thread(captureAcousticEcho, "captureEcho");
        Thread threadCapture = new Thread(captureAcousticEcho, "captureEcho");
        List<float[]> listOfRecords = new ArrayList<>();

        //ChirpEmitterBisccitAttempt.playSound(CHIRP_FREQUENCY, chirpRepeat);

        TimerTask task = new TimerTask() {
            @Override
            public void run() {
                ChirpEmitterBisccitAttempt.playSound(duration);
            }
        };

        Timer timer = new Timer("Timer");
        //audioRecord.startRecording();
        //timer.scheduleAtFixedRate(task, 1L, 100L);
        timer.schedule(task, 1L);
        threadCapture.start();

        try {
            Thread.sleep((long)(this.duration * 1000));
            captureAcousticEcho.stopCapture();
            //timer.cancel();
            audioRecord.stop();
            audioRecord.release();
            captureAcousticEcho.stopThread();

            Log.i("BUFFER", "" + Util.printArray(captureAcousticEcho.buffer, 30000, 31000));

            listOfRecords.add(Arrays.copyOf(captureAcousticEcho.buffer, captureAcousticEcho.buffer.length));

//            TextView label = (TextView) activity.findViewById(R.id.label_of_room);
//            label.setText(Util.printArray(captureAcousticEcho.buffer, 30000, 30100));


            Log.i("SHORTS LENGTH", "" + listOfRecords.get(0).length);

            callback.run(activity, listOfRecords);

        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }

        //chirpEmitter.destroy();
    }

    private AudioRecord createAudioRecord() {

        if (ContextCompat.checkSelfPermission(activity,
                Manifest.permission.RECORD_AUDIO)
                != PackageManager.PERMISSION_GRANTED) {

            // Should we show an explanation?
            if (ActivityCompat.shouldShowRequestPermissionRationale(activity,
                    Manifest.permission.RECORD_AUDIO)) {

                // Show an expanation to the user *asynchronously* -- don't block
                // this thread waiting for the user's response! After the user
                // sees the explanation, try again to request the permission.

            } else {

                // No explanation needed, we can request the permission.

                ActivityCompat.requestPermissions(activity,
                        new String[]{Manifest.permission.RECORD_AUDIO},
                        1);

                // MY_PERMISSIONS_REQUEST_READ_CONTACTS is an
                // app-defined int constant. The callback method gets the
                // result of the request.
            }
        }

        AudioRecord audioRecord = new AudioRecord(
                MediaRecorder.AudioSource.MIC,
                44100,
                AudioFormat.CHANNEL_IN_MONO,
                AudioFormat.ENCODING_PCM_FLOAT,
                (int) (Globals.SAMPLE_RATE * duration) // sampleRate*duration*2*repeats
        );
//        System.out.println(audioRecord.getBufferSizeInFrames());
        return audioRecord;
    }

}
