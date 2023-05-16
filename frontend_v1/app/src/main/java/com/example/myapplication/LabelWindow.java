package com.example.myapplication;


import android.Manifest;
import android.app.Activity;
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

    private final int CHIRP_FREQUENCY = 19500;

    // Back is disabled during labelling
    boolean training = false;
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
        TextView label = (TextView) findViewById(R.id.label_of_room);
        TextView labelOfBuilding = (TextView) findViewById(R.id.label_of_building);
        TextView sent_label = (TextView) findViewById(R.id.sent_label);
        Button button_start = (Button) findViewById(R.id.button_submit);
        TextView progress = (TextView) findViewById(R.id.textView4);

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
                    int repeatChirp = 502;
//                  
                    ChirpEmitterBisccitAttempt chirpEmitter = new ChirpEmitterBisccitAttempt(CHIRP_FREQUENCY);
                  
                    AudioRecord audioRecord = createAudioRecord();
                    System.out.println(audioRecord.getState());
                    CaptureAcousticEcho captureAcousticEcho = new CaptureAcousticEcho(audioRecord, repeatChirp);
//                    Thread threadCapture = new Thread(captureAcousticEcho, "captureEcho");
                    Thread threadCapture = new Thread(captureAcousticEcho, "captureEcho");
                    List<short[]> listOfRecords = new ArrayList<>();
                    TimerTask task = new TimerTask() {
                        int count = 0;
                        @Override
                        public void run() {
                            chirpEmitter.playOnce();
                        }
                    };

                    Timer timer = new Timer("Timer");
                    audioRecord.startRecording();
                    timer.scheduleAtFixedRate(task, 1L, 100L);
                    threadCapture.start();

                    try {
                        Thread.sleep(100L*repeatChirp);
                        captureAcousticEcho.stopCapture();
                        timer.cancel();
                        audioRecord.stop();
                        audioRecord.release();
                        captureAcousticEcho.stopThread();
                        listOfRecords.add(Arrays.copyOf(captureAcousticEcho.buffer, captureAcousticEcho.buffer.length));

                        audioRecord = null;

                        buildAndSendRequest(
                                String.valueOf(label.getText()),
                                listOfRecords
                                        .stream()
                                        .filter(x -> sumUp(x) > 0)
                                        .collect(Collectors.toList()),
                                String.valueOf(labelOfBuilding.getText())
                        );


                    } catch (InterruptedException | JSONException | IOException e) {
                        throw new RuntimeException(e);
                    }

                    chirpEmitter.destroy();
                    training = false;
                }
            }

            public int sumUp(short[] array){
                for (short value : array) {
                    if (value > 0) {
                        return 1;
                    }
                }
                return -1;
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
                (int) (44100*0.1*200) // sampleRate*duration*2*repeats
        );
//        System.out.println(audioRecord.getBufferSizeInFrames());
        return audioRecord;
    }

    private void buildAndSendRequest(String placeLabel, List<short[]> listOfRecords, String building) throws IOException, JSONException {
        Log.i("BuildAndSendRequest", "Sending request");
        CronetProviderInstaller.installProvider(this);
        CronetEngine.Builder myBuilder = new CronetEngine.Builder(this);
        CronetEngine cronetEngine = myBuilder.build();

        Executor executor = Executors.newSingleThreadExecutor();
        String requestUrl = " http://192.168.56.1:5000/add_new_location_point";
        Uri.Builder uriBuilder = Uri.parse(requestUrl).buildUpon();
        uriBuilder.appendQueryParameter("placeLabel", placeLabel);
        uriBuilder.appendQueryParameter("buildingLabel", building);
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
}