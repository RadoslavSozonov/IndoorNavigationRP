package com.example.myapplication;


import android.Manifest;
import android.app.Activity;
import android.content.pm.PackageManager;
import android.media.AudioAttributes;
import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.AudioTrack;
import android.media.MediaRecorder;
import android.os.Bundle;
import android.util.DisplayMetrics;
import android.util.Log;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.TextView;

import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.example.myapplication.AudioTrack.CaptureAcousticEcho;
import com.example.myapplication.AudioTrack.EmitChirpStackOFVersion;

import java.lang.reflect.Array;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Timer;
import java.util.TimerTask;


public class LabelWindow extends Activity {
    // Back is disabled during labelling
    boolean training = false;
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
        TextView label = (TextView) findViewById(R.id.label_of_room);
        TextView sent_label = (TextView) findViewById(R.id.sent_label);
        Button button_start = (Button) findViewById(R.id.button_submit);

        int currentapiVersion = android.os.Build.VERSION.SDK_INT;
        if (currentapiVersion > android.os.Build.VERSION_CODES.LOLLIPOP){

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

        // Start labeling callback
        button_start.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if(!training) {
                    // get and set rooms label from user input
                    String label_text = label.getText().toString();
                    sent_label.setText(label_text);
                    // Disable back button while labeling
                    training = true;
                    // TODO: chirp and receive 500 echos, then send them to server
                    int freq1 = 21500;
                    int freq2 = 22000;
                    float duration = 0.002f;
                    int repeatChirp = 101;
                    EmitChirpStackOFVersion chirpStackOFVersion = new EmitChirpStackOFVersion(freq1, freq2, duration);
//                    chirpStackOFVersion.playSoundOnce();
                    AudioRecord audioRecord = createAudioRecord(repeatChirp);
                    System.out.println(audioRecord.getState());
                    CaptureAcousticEcho captureAcousticEcho = new CaptureAcousticEcho(audioRecord);
//                    Thread threadCapture = new Thread(captureAcousticEcho, "captureEcho");
                    Thread threadCapture = new Thread(captureAcousticEcho, "captureEcho");
                    List<short[]> listOfRecords = new ArrayList<>();
                    TimerTask task = new TimerTask() {
                        @Override
                        public void run() {
//                            System.out.println(captureAcousticEcho.buffer);
                            listOfRecords.add(Arrays.copyOf(captureAcousticEcho.buffer, captureAcousticEcho.buffer.length));
                            captureAcousticEcho.stopCapture();
                            captureAcousticEcho.startCapture();
                            chirpStackOFVersion.playSoundOnce();

                        }
                    };

                    Timer timer = new Timer("Timer");
                    threadCapture.start();

                    audioRecord.startRecording();
                    timer.scheduleAtFixedRate(task, 0L, 100L);

                    try {
                        Thread.sleep(100L*repeatChirp);
                        timer.cancel();
                        audioRecord.stop();
                        audioRecord.release();
                        captureAcousticEcho.stopThread();

                        audioRecord = null;


                    } catch (InterruptedException e) {
                        throw new RuntimeException(e);
                    }
//                    for(short[] array: listOfRecords){
//                        System.out.println(array);
//                    }
                    new Thread(() -> {
                        ServerCommunication.addRoom(new Room(listOfRecords, label_text, "myBuilding"));
                    }).start();
                    training = false;
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
                if(!training) {
                    finish();
                }
            }
        });
    }

    private AudioRecord createAudioRecord(int repeats) {
        int bufferSize = AudioRecord.getMinBufferSize(
                44100,
                AudioFormat.CHANNEL_IN_MONO,
                AudioFormat.ENCODING_PCM_16BIT
        );


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
                (int) (44100*0.1*2*repeats) // sampleRate*duration*2*repeats
        );
//        System.out.println(audioRecord.getBufferSizeInFrames());
        return audioRecord;
    }
}

/*
public void playCodeFromChatGPT4(int freq1, int freq2, float duration) {
                int SAMPLE_RATE = 44100; // Hz
                int CHIRP_FREQ_START = freq1; // Hz
                int CHIRP_FREQ_END = freq2; // Hz
                float CHIRP_DURATION = duration; // ms
                int BUFFER_SIZE = (int) (SAMPLE_RATE * CHIRP_DURATION); // samples

                // Create AudioTrack object
                AudioTrack audioTrack = new AudioTrack.Builder()
                        .setAudioAttributes(new AudioAttributes.Builder()
                                .setUsage(AudioAttributes.USAGE_ALARM)
                                .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                                .build())
                        .setAudioFormat(new AudioFormat.Builder()
                                .setEncoding(AudioFormat.ENCODING_PCM_16BIT)
                                .setSampleRate(SAMPLE_RATE)
                                .setChannelMask(AudioFormat.CHANNEL_OUT_MONO)
                                .build())
                        .setBufferSizeInBytes(BUFFER_SIZE * 2)
                        .build();

                // Create buffer
                short[] buffer = new short[BUFFER_SIZE];

                // Fill buffer with chirp waveform
                for (int i = 0; i < BUFFER_SIZE; i++) {
                    double t = (double) i / SAMPLE_RATE;
                    double freq = CHIRP_FREQ_START + (CHIRP_FREQ_END - CHIRP_FREQ_START) * t / (CHIRP_DURATION );
                    // fo + ((f1 - fo) * t)/T
                    double y = Math.sin(2 * Math.PI * freq * t);
                    //2*PI*t * (fo + ((f1 - fo) * t)/T)
                    //2*PI*t*fo + 2*PI*t^2*c -> c = (f1-fo)/T
                    //2*PI*t*fo + 2*PI*t^2*c
                    buffer[i] = (short) (y * Short.MAX_VALUE);
                }

                // Write buffer to AudioTrack and start playback
                audioTrack.write(buffer, 0, BUFFER_SIZE);
                audioTrack.play();
                System.out.println("Sound played Chat");
            }
 */