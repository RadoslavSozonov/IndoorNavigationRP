package com.example.myapplication;


import android.app.Activity;
import android.media.AudioAttributes;
import android.media.AudioFormat;
import android.media.AudioTrack;
import android.os.Bundle;
import android.util.DisplayMetrics;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.TextView;

import com.example.myapplication.AudioTrack.EmitChirpStackOFVersion;

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
                    int freq1 = 19500;
                    int freq2 = 20500;
                    float duration = 0.002f;
                    int repeatChirp = 50;
                    EmitChirpStackOFVersion chirpStackOFVersion = new EmitChirpStackOFVersion(freq1, freq2, duration);
//                    chirpStackOFVersion.playSoundOnce();
                    TimerTask task = new TimerTask() {
                        @Override
                        public void run() {
                            chirpStackOFVersion.playSoundOnce();
                        }
                    };

                    Timer timer = new Timer("Timer");

                    timer.scheduleAtFixedRate(task, 0L, 100L);

                    try {
                        Thread.sleep(100L*repeatChirp);
                        timer.cancel();
                    } catch (InterruptedException e) {
                        throw new RuntimeException(e);
                    }

                    training = false;
                }
            }

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
}
