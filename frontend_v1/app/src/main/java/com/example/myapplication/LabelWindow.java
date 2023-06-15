package com.example.myapplication;


import android.Manifest;
import android.app.Activity;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.util.DisplayMetrics;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.TextView;

import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.example.myapplication.AudioTrack.DataRecorder;
import com.example.myapplication.RequestCallbacks.LabelCallback;


public class LabelWindow extends Activity {



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

        TextView duration = (TextView) findViewById(R.id.duration);
        TextView frequency = (TextView) findViewById(R.id.frequency);


        int currentapiVersion = android.os.Build.VERSION.SDK_INT;
        if (currentapiVersion > android.os.Build.VERSION_CODES.LOLLIPOP){

            if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) !=
                    PackageManager.PERMISSION_GRANTED) {

                // Should we show an explanation?
                if (ActivityCompat.shouldShowRequestPermissionRationale(this,
                        Manifest.permission.RECORD_AUDIO)) {

                    // Show an explanation to the user *asynchronously* -- don't block
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

                    Globals.LABEL_DURATION = Double.parseDouble(duration.getText().toString());
                    Globals.CHIRP_FREQUENCY = Integer.parseInt(frequency.getText().toString());

                    DataRecorder dataRecorder = new DataRecorder(Globals.LABEL_DURATION, getThis(), new LabelCallback(String.valueOf(label.getText()), String.valueOf(labelOfBuilding.getText())));

                    dataRecorder.recordData();

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

    private Activity getThis() {
        return this;
    }
}