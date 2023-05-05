package com.example.myapplication;


import static android.view.View.VISIBLE;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.util.DisplayMetrics;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.TextView;


public class TopFiveWindow extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.popup_topfive);

        // Components
        RadioButton button_1 = (RadioButton) findViewById(R.id.radio_button_1);
        RadioButton button_2 = (RadioButton) findViewById(R.id.radio_button_2);
        RadioButton button_3 = (RadioButton) findViewById(R.id.radio_button_3);
        RadioButton button_4 = (RadioButton) findViewById(R.id.radio_button_4);
        RadioButton button_5 = (RadioButton) findViewById(R.id.radio_button_5);
        RadioButton button_6 = (RadioButton) findViewById(R.id.radio_button_6);
        Button button_submit = (Button) findViewById(R.id.button_submit);
        TextView custom_label = (TextView) findViewById(R.id.custom_label);

        // Set the room labels
        Intent intent = getIntent();
        String[] room_labels = intent.getStringArrayExtra("room_labels");

        // setup submit callback
        button_submit.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String room_label = "";

                if(button_1.isChecked()) {
                    room_label = room_labels[0];
                } else if (button_2.isChecked()) {
                    room_label = room_labels[1];
                } else if (button_3.isChecked()) {
                    room_label = room_labels[2];
                } else if (button_4.isChecked()) {
                    room_label = room_labels[3];
                } else if (button_5.isChecked()) {
                    room_label = room_labels[4];
                } else if (button_6.isChecked()) {
                    room_label = custom_label.getText().toString();
                }
                if (!room_label.equals("")) {
                    // TODO: send the label to the server
                    finish();
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
                    finish();
            }
        });
    }


}
