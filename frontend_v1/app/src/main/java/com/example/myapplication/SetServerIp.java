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
import android.util.DisplayMetrics;
import android.util.Log;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.TextView;



public class SetServerIp extends Activity {

    private final int CHIRP_FREQUENCY = 5000;

    // Back is disabled during labelling
    boolean training = false;

    @Override
    public void onBackPressed() {
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.popup_server);

        // Get layout components
        TextView server_ip = (TextView) findViewById(R.id.server_ip);
        Button button_submit = (Button) findViewById(R.id.button_submit);

        // Start labeling callback
        button_submit.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent returnIntent = new Intent();
                returnIntent.putExtra("server_ip", server_ip.getText().toString());
                setResult(Activity.RESULT_OK, returnIntent);
                finish();
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


    }
}