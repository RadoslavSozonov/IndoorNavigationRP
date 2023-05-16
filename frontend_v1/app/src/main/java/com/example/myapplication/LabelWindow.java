package com.example.myapplication;


import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.MediaRecorder;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.util.DisplayMetrics;
import android.util.Log;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.TextView;

import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import com.example.myapplication.AudioTrack.ChirpEmitterBisccitAttempt;

import com.example.myapplication.RequestCallbacks.MyUrlRequestCallback;
import com.google.android.gms.net.CronetProviderInstaller;

import org.chromium.net.CronetEngine;
import org.chromium.net.UploadDataProvider;
import org.chromium.net.UploadDataProviders;
import org.chromium.net.UrlRequest;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Timer;
import java.util.TimerTask;
import java.util.concurrent.BrokenBarrierException;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;


public class LabelWindow extends Activity {


    // Back is disabled during labelling
    private boolean training = false;
    private CyclicBarrier cyclicBarrier = new CyclicBarrier(1);
    @Override
    public void onBackPressed() {
        System.out.println("Hey");
        if (!training) {
            super.onBackPressed();
        }
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.popup_label);

        // Get layout components
        TextView room_label = (TextView) findViewById(R.id.label_of_room);
        TextView building_label = (TextView) findViewById(R.id.label_of_building);
        TextView sent_label = (TextView) findViewById(R.id.sent_label);
        Button button_start = (Button) findViewById(R.id.button_submit);
        TextView progress = (TextView) findViewById(R.id.textView4);

        // get server IP
        Intent intent = getIntent();
        String server_ip = intent.getStringExtra("server_ip");

        int currentapiVersion = android.os.Build.VERSION.SDK_INT;
        if (currentapiVersion > android.os.Build.VERSION_CODES.LOLLIPOP) {

            if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) !=
                    PackageManager.PERMISSION_GRANTED) {

                // Should we show an explanation?
                if (ActivityCompat.shouldShowRequestPermissionRationale(this,
                        Manifest.permission.RECORD_AUDIO)) {

                    // Show an expanation to the user *asynchronously* -- don't block
                    // this thread waiting for the user's response! After the user
                    // sees the explanation, try again to request the permission.

                } else {

                    // No explanation needed, we can request the permission.

                    ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.RECORD_AUDIO}, 1);
                }
            }
        }

        Handler handler = new Handler();
        button_start.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (!training) {
                    // get and set rooms label from user input
                    String label_room_text = room_label.getText().toString();
                    String label_building_text = building_label.getText().toString();
                    sent_label.setText(label_building_text + ": " + label_room_text);
                    progress.setText("In progress");
                    // Disable back button while labeling
                    training = true;

                    new Thread(new Runnable() {
                        @Override
                        public void run() {
                            AudioRecord audioRecord = createAudioRecord();
                            int buffer_size = (int) (Globals.SAMPLE_RATE * Globals.RECORDING_INTERVAL * Globals.REPEAT_CHIRP);
                            short[] buffer = new short[buffer_size];

                            List<short[]> listOfRecords = new ArrayList<>();

                            audioRecord.startRecording();
                            new Thread(new Runnable() {
                                @Override
                                public void run() {
                                    try {
                                        cyclicBarrier.await();

                                        audioRecord.read(buffer, 0, buffer_size);
                                    } catch (BrokenBarrierException e) {
                                        throw new RuntimeException(e);
                                    } catch (InterruptedException e) {
                                        throw new RuntimeException(e);
                                    }

                                }
                            }).start();

                            ChirpEmitterBisccitAttempt.playSound(Globals.CHIRP_FREQUENCY, Globals.REPEAT_CHIRP, cyclicBarrier);

                            listOfRecords.add(Arrays.copyOf(buffer, buffer_size));
                            audioRecord.stop();
                            audioRecord.release();

                            new Thread(() -> {
                                ServerCommunication.addRoom(new Room(listOfRecords, label_room_text.trim(), label_building_text.trim()), server_ip);
                            }).start();
                            runOnUiThread(new Runnable() {
                                @Override
                                public void run() {
                                    progress.setText("Done!");
                                }
                            });
                            training = false;
                        }
                    }).start();

                }
            }
        });

        // Setup pop up layout
        DisplayMetrics displayMetrics = new DisplayMetrics();
        getWindowManager().getDefaultDisplay().getMetrics(displayMetrics);

        int width = displayMetrics.widthPixels;
        int height = displayMetrics.heightPixels;

        getWindow().setLayout((int) (width * 0.8), (int) (height * 0.8));

        WindowManager.LayoutParams layoutParams = getWindow().getAttributes();
        layoutParams.dimAmount = 0.35f;
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_DIM_BEHIND);
        getWindow().setAttributes(layoutParams);


        // Make a back button
        Button button_back = (Button) findViewById(R.id.button_back);
        button_back.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (!training) {
                    finish();
                }
            }
        });
    }

    private AudioRecord createAudioRecord() {

        if (ContextCompat.checkSelfPermission(this,
                Manifest.permission.RECORD_AUDIO)
                != PackageManager.PERMISSION_GRANTED) {

            // Should we show an explanation?
            if (ActivityCompat.shouldShowRequestPermissionRationale(this,
                    Manifest.permission.RECORD_AUDIO)) {

                // Show an expanation to the user *asynchronously* -- don't block
                // this thread waiting for the user's response! After the user
                // sees the explanation, try again to request the permission.

            } else {

                // No explanation needed, we can request the permission.

                ActivityCompat.requestPermissions(this,
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
                AudioFormat.ENCODING_PCM_16BIT,
                (int) (44100 * 0.1 * 2 * 100) // sampleRate*duration*2*repeats
        );
//        System.out.println(audioRecord.getBufferSizeInFrames());
        return audioRecord;
    }
}