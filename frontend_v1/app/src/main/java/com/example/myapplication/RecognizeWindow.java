package com.example.myapplication;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.MediaRecorder;
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

public class RecognizeWindow extends Activity {
    private CyclicBarrier cyclicBarrier = new CyclicBarrier(2);
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.popup_recognize);

        // Get layout components
        TextView popup_text = (TextView) findViewById(R.id.popup_text);
        Intent intent = getIntent();
        String server_ip = intent.getStringExtra("server_ip");

        new Thread(new Runnable() {
            @Override
            public void run() {
                AudioRecord audioRecord = createAudioRecord();
                int buffer_size = (int) (Globals.SAMPLE_RATE * Globals.RECORDING_INTERVAL * Globals.REPEAT_CHIRP_RECOGNIZE);
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

                ChirpEmitterBisccitAttempt.playSound(Globals.CHIRP_FREQUENCY, Globals.REPEAT_CHIRP_RECOGNIZE, cyclicBarrier);

                listOfRecords.add(Arrays.copyOf(buffer, buffer_size));
                audioRecord.stop();
                audioRecord.release();
                String label = ServerCommunication.recognizeRoom(new Room(listOfRecords, "Unknown", "Unknown"), server_ip);
                runOnUiThread(() -> popup_text.setText(label));
            }
        }).start();



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
        Button button_back = (Button) findViewById(R.id.button_back_popup);
        button_back.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
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
