package com.example.myapplication;


import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.media.AudioAttributes;
import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.AudioTrack;
import android.media.MediaRecorder;
import android.net.Uri;
import android.os.Bundle;
import android.util.DisplayMetrics;
import android.util.Log;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.TextView;
import org.json.JSONArray;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import com.example.myapplication.AudioTrack.ChirpEmitterBisccitAttempt;

import com.example.myapplication.AudioTrack.CaptureAcousticEcho;
import com.example.myapplication.AudioTrack.EmitChirpStackOFVersion;
import com.example.myapplication.RequestCallbacks.MyUrlRequestCallback;
import com.google.android.gms.net.CronetProviderInstaller;

import org.chromium.net.CronetEngine;
import org.chromium.net.UploadDataProvider;
import org.chromium.net.UploadDataProviders;
import org.chromium.net.UrlRequest;
import org.json.JSONArray;
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
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;
import java.util.stream.Collectors;
import java.util.stream.Stream;



public class LabelWindow extends Activity {

    private final int CHIRP_FREQUENCY = 5000;

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
        TextView room_label = (TextView) findViewById(R.id.label_of_room);
        TextView building_label = (TextView) findViewById(R.id.label_of_room);
        TextView sent_label = (TextView) findViewById(R.id.sent_label);
        Button button_start = (Button) findViewById(R.id.button_submit);
        TextView progress = (TextView) findViewById(R.id.textView4);


        // get server IP
        Intent intent = getIntent();
        String server_ip = intent.getStringExtra("server_ip");

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
                    String label_room_text = room_label.getText().toString();
                    String label_building_text = building_label.getText().toString();
                    sent_label.setText(label_room_text + " " + label_building_text);
                    // Disable back button while labeling
                    training = true;
                    // TODO: chirp and receive 500 echos, then send them to server
                    int repeatChirp = 5;

                    ChirpEmitterBisccitAttempt chirpEmitter = new ChirpEmitterBisccitAttempt(CHIRP_FREQUENCY);
                    AudioRecord audioRecord = createAudioRecord();

                    CaptureAcousticEcho captureAcousticEcho = new CaptureAcousticEcho(audioRecord);
                    Thread threadCapture = new Thread(captureAcousticEcho, "captureEcho");
                    List<short[]> listOfRecords = new ArrayList<>();

                    audioRecord.startRecording();
                    threadCapture.start();

                    for(int i = 0; i < repeatChirp; i++) {
                        captureAcousticEcho.stopCapture();
                        chirpEmitter.playOnce();
                        try {
                            Thread.sleep(100L);
                        } catch (InterruptedException e) {
                            throw new RuntimeException(e);
                        }
                        captureAcousticEcho.startCapture();
                        listOfRecords.add(Arrays.copyOf(captureAcousticEcho.buffer, captureAcousticEcho.buffer.length));
                    }

                    audioRecord.stop();
                    audioRecord.release();
                    captureAcousticEcho.stopThread();

                    new Thread(() -> {
                        ServerCommunication.addRoom(new Room(listOfRecords, label_room_text.trim(), label_building_text.trim()), server_ip);
                    }).start();

                    chirpEmitter.destroy();

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
                (int) (44100*0.1*2*100) // sampleRate*duration*2*repeats
        );
//        System.out.println(audioRecord.getBufferSizeInFrames());
        return audioRecord;
    }

    private void buildAndSendRequest(String placeLabel, List<short[]> listOfRecords) throws IOException, JSONException {
        Log.i("BuildAndSendRequest", "Sending request");
        CronetProviderInstaller.installProvider(this);
        CronetEngine.Builder myBuilder = new CronetEngine.Builder(this);
        CronetEngine cronetEngine = myBuilder.build();

        Executor executor = Executors.newSingleThreadExecutor();
        String requestUrl = "http://145.94.200.217:5000/add_new_location_point";
        Uri.Builder uriBuilder = Uri.parse(requestUrl).buildUpon();
        uriBuilder.appendQueryParameter("placeLabel", placeLabel);
        String urlWithQueryParams = uriBuilder.build().toString();

        int count = 1;
        JSONObject jsonObject = new JSONObject();
        for(short[] array: listOfRecords){
            jsonObject.put(String.valueOf(count), Arrays.toString(array));
            count++;
        }
        String requestBody = jsonObject.toString();

        UploadDataProvider uploadDataProvider = UploadDataProviders.create(requestBody.getBytes(), 0, requestBody.getBytes().length);

        UrlRequest.Builder requestBuilder = cronetEngine
                .newUrlRequestBuilder(
                        urlWithQueryParams, new MyUrlRequestCallback(), executor)
                .setHttpMethod("POST")
                .addHeader("Content-Type", "application/json")
                .setUploadDataProvider(uploadDataProvider, executor);

        UrlRequest request = requestBuilder.build();
        request.start();
        Log.i("BuildAndSendRequest", "request.start() executed");
    }

    public static String getParamsString(Map<String, List<short[]>> params)
            throws UnsupportedEncodingException {
        StringBuilder result = new StringBuilder();

        for (Map.Entry<String, List<short[]>> entry : params.entrySet()) {
            result.append(URLEncoder.encode(entry.getKey(), "UTF-8"));
            result.append("=");
            result.append(URLEncoder.encode(entry.getValue().toString(), "UTF-8"));
            result.append("&");
        }

        String resultString = result.toString();
        return resultString.length() > 0
                ? resultString.substring(0, resultString.length() - 1)
                : resultString;
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