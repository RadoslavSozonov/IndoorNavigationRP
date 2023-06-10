package com.example.myapplication;


import android.Manifest;
import android.app.Activity;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.MediaRecorder;
import android.net.wifi.ScanResult;
import android.net.wifi.WifiManager;
import android.os.Bundle;
import android.util.DisplayMetrics;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.TextView;

import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.example.myapplication.AudioTrack.ChirpEmitterBisccitAttempt;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.BrokenBarrierException;
import java.util.concurrent.CyclicBarrier;


public class LabelWindow extends Activity {


    // Back is disabled during labelling
    private boolean waitingForScan = true;
    private boolean training = false;
    private CyclicBarrier cyclicBarrier = new CyclicBarrier(2);

    private List<WiFiFingerprint> wifi_list;
    @Override
    public void onBackPressed() {
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
        Button button_train = (Button) findViewById(R.id.button_train);
        TextView progress = (TextView) findViewById(R.id.textView4);


//        WifiRttManager wifiRttManager = (WifiRttManager) getSystemService(Context.WIFI_RTT_RANGING_SERVICE);
//        System.out.println(this.getPackageManager().hasSystemFeature(PackageManager.FEATURE_WIFI_RTT));


//        IntentFilter filter =
//                new IntentFilter(WifiRttManager.ACTION_WIFI_RTT_STATE_CHANGED);
//        BroadcastReceiver myReceiver = new BroadcastReceiver() {
//            @Override
//            public void onReceive(Context context, Intent intent) {
//                if (wifiRttManager.isAvailable()) {
//
//                } else {
//
//                }
//            }
//        };
//        this.registerReceiver(myReceiver, filter);


        WifiManager wifiManager = (WifiManager) this.getSystemService(Context.WIFI_SERVICE);
        BroadcastReceiver wifiScanReceiver = new BroadcastReceiver() {
            @Override
            public void onReceive(Context c, Intent intent) {
                boolean success = intent.getBooleanExtra(
                        WifiManager.EXTRA_RESULTS_UPDATED, false);
                if (success) {

                    List<ScanResult> results = wifiManager.getScanResults();
                    List<WiFiInfo> fingerprint = new ArrayList<>();
                    for (ScanResult scanResult : results) {
                        int level = WifiManager.calculateSignalLevel(scanResult.level, 100);
//                        System.out.println(scanResult.SSID);
//                        System.out.println(scanResult.BSSID);
                        fingerprint.add(new WiFiInfo(scanResult.BSSID, scanResult.SSID, level));
                    }
                    wifi_list.add(new WiFiFingerprint(fingerprint));
                    waitingForScan = false;


                } else {
                    // scan failure handling
                    System.out.println("not success :(");
                }
            }
        };
        IntentFilter intentFilter = new IntentFilter();
        intentFilter.addAction(WifiManager.SCAN_RESULTS_AVAILABLE_ACTION);
        this.registerReceiver(wifiScanReceiver, intentFilter);



        // get server IP
        Intent intent = getIntent();
        String server_ip = intent.getStringExtra("server_ip");


        button_start.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (!training) {
                    if (room_label.getText().toString().trim().isEmpty() || building_label.getText().toString().trim().isEmpty()) {
                        return;
                    }
                    // get and set rooms label from user input
                    String label_room_text = room_label.getText().toString();
                    String label_building_text = building_label.getText().toString();
                    sent_label.setText(label_building_text + ": " + label_room_text);
                    progress.setText("In progress");
                    // Disable back button while labeling
                    training = true;

                    wifi_list = new ArrayList<>();
                    new Thread(new Runnable() {

                        @Override
                        public void run() {

                            for(int j = 0; j < 10; j++) {
                                // Collect WiFi Data
                                wifi_list = new ArrayList<>();
                                for (int i = 0; i < Globals.REPEAT_WIFI; i++) {
                                    waitingForScan = true;
                                    final int counter = i;
                                    runOnUiThread(new Runnable() {
                                        @Override
                                        public void run() {
                                            progress.setText(String.valueOf(counter) + "/" + String.valueOf(Globals.REPEAT_WIFI));  // THIS LINE CRASHES THE PROGRAM
                                        }
                                    });
                                    boolean success = wifiManager.startScan();
                                    if (!success) {
                                        // scan failure handling
                                        System.out.println("No success here :(");
                                    }
                                    while(waitingForScan);
                                    try {
                                        Thread.sleep(Globals.THROTTLE_WIFI_MS);
                                    } catch (InterruptedException e) {
                                        throw new RuntimeException(e);
                                    }
                                }

                                runOnUiThread(new Runnable() {
                                    @Override
                                    public void run() {
                                        progress.setText("emitting chirps...");  // THIS LINE CRASHES THE PROGRAM
                                    }
                                });
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
                                runOnUiThread(new Runnable() {
                                    @Override
                                    public void run() {
                                        progress.setText("processing...");  // THIS LINE CRASHES THE PROGRAM
                                    }
                                });
                                ServerCommunication.addRoom(new Room(listOfRecords, label_room_text.trim(), label_building_text.trim(), wifi_list), server_ip);
                            }
                            training = false;
                            runOnUiThread(new Runnable() {
                                @Override
                                public void run() {
                                    progress.setText("Done!");
                                }
                            });
                        }
                    }).start();


                }
            }
        });
        button_train.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                progress.setText("In progress");
                new Thread(() -> {
                    if (!training) {
                        training = true;
                        String response = ServerCommunication.startTraining(server_ip);
                        training = false;
                        runOnUiThread(new Runnable() {
                            @Override
                            public void run() {
                                progress.setText(response);
                            }
                        });
                    }
                }).start();
            }
        });
        // Setup pop up layout
        DisplayMetrics displayMetrics = new DisplayMetrics();
        getWindowManager().getDefaultDisplay().getMetrics(displayMetrics);

        int width = displayMetrics.widthPixels;
        int height = displayMetrics.heightPixels;

        getWindow().setLayout((int) (width * 0.8), (int) (height * 0.8));
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

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
                    unregisterReceiver(wifiScanReceiver);
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