package com.example.myapplication;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.util.DisplayMetrics;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.TextView;

public class RecognizeWindow extends Activity {

    public static RecognizeWindow instance;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        instance = this;
        super.onCreate(savedInstanceState);
        setContentView(R.layout.popup_recognize);

        // Get layout components
        TextView popup_title = (TextView) findViewById(R.id.popup_title);
        TextView popup_text = (TextView) findViewById(R.id.popup_text);

        // set the text of the popup
        Intent intent = getIntent();
        popup_title.setText(intent.getStringExtra("title"));
        popup_text.setText(intent.getStringExtra("text"));

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


}
