package com.example.myapplication;

import androidx.activity.result.ActivityResult;
import androidx.activity.result.ActivityResultCallback;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AppCompatActivity;

import android.app.Activity;
import android.content.Intent;
import android.content.res.AssetFileDescriptor;
import android.content.res.AssetManager;
import android.content.res.Resources;
import android.media.AudioFormat;
import android.media.AudioManager;
import android.media.AudioTrack;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import java.io.BufferedReader;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.lang.reflect.Field;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

public class MainActivity extends AppCompatActivity {
    private String rooms = "";

    private boolean useStaticIp = true;
    private String server_ip = "145.94.225.159";

    private Activity activity = this;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Components of the layout
        Button train_model = (Button) findViewById((R.id.trainModel));
        Button button_recognize = (Button) findViewById(R.id.button_recognize);
        Button button_label_room = (Button) findViewById(R.id.button_label_room);
        Button button_top_5 = (Button) findViewById(R.id.button_top_5);
        TextView list_of_rooms = (TextView) findViewById(R.id.list_of_rooms);

        list_of_rooms.setText(rooms);


        // Make a pop up showing the room label
        Intent server_ip_intent = new Intent(MainActivity.this, SetServerIp.class);
        train_model.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Make a pop up asking for the label
                Intent intent = new Intent(MainActivity.this, TrainModel.class);

                startActivity(intent);
            }
        });


        ActivityResultLauncher<Intent> serverActivityIpLauncher =
                registerForActivityResult(new
                                ActivityResultContracts.StartActivityForResult(),
                        (result) -> {
                            server_ip = result.getData().getStringExtra("server_ip");

                            new Thread(new GetRoomsExecutor(rooms, this, server_ip)).start();
                            // code to process data from activity called
                        }
                );
        if(!useStaticIp) {
            serverActivityIpLauncher.launch(server_ip_intent);
        }
        // Popup for recognizing the current room
        button_recognize.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // TODO: get the label of the room
//                "android.resource://"+ "com.example.phone"+ "/" + "raw/dennis"
                String filePath = "android.resource://"+ "com.example.myapplication"+ "/" + "in.txt";
//                Field[] fields=R.raw.class.getFields();
//                R.raw.class.getResourceAsStream();
//                for(int count=0; count < fields.length; count++){
//                    Log.i("Raw Asset: ", fields[count].getName());
//                }
                short[] audioData = loadAudioData(filePath);
                System.out.println("Data collected");
                ServerCommunicationCronetEngine.getNameOfModel(activity, "145.94.238.95");
                while (ModelName.modelNames.size() == 0){
                    continue;
                }
                int sampleRate = 4410;
                int chirps = audioData.length/sampleRate;
                System.out.println(chirps);
//                System.out.println(na);
                for(String modelName: ModelName.modelNames){
                    Log.i("Model Name", modelName.substring(1, modelName.length()-1));
                    int timeOnBackend = 0;
                    int timeReqRes = 0;
                    for(int i = 2; i <= chirps - 2; i++){
                        short[] chirp = new short[8820];
                        for(int y = 0, z = i*sampleRate; y<8820; y++){
                            chirp[y] = audioData[z+y];
                        }
                        while (i-2 != ResponseTimes.backendResponseTime.size()){
                            continue;
                        }
                        List<Integer> times = ServerCommunicationCronetEngine.testPlace(chirp, modelName.substring(1, modelName.length()-1), activity,"145.94.211.247");
                    }
                    Log.i("Backend Time", String.valueOf(ResponseTimes.backendResponseTime.stream().mapToDouble(a->a).average()));
                    Log.i("Response Time", String.valueOf(ResponseTimes.requestResponseTime.stream().mapToDouble(a->a).average()));

                }

//                String room_label = "room 1";
//
//
//                // Make a pop up showing the room label
//                Intent intent = new Intent(MainActivity.this, RecognizeWindow.class);
//                intent.putExtra("title", "The room label is:");
//                intent.putExtra("text", room_label);
//                startActivity(intent);
            }

            public short[] loadAudioData(String name){
//                InputStream inputStream = new

//                Resources resources = getResources();
//                InputStream iS;
//                Field[] fields=R.raw.class.getFields();
//                for(int i = 0; i<fields.length;i++){
//                    System.out.println(fields[i].getName());
//                    int rID = 0;
//                    try {
//                        rID = fields[i].getInt(fields[i]);
//                    } catch (IllegalAccessException e) {
//                        throw new RuntimeException(e);
//                    }
//                    //get the file as a stream
//                    iS = resources.openRawResource(rID);
//
//                    //create a buffer that has the same size as the InputStream
//                    byte[] buffer = new byte[0];
//                    try {
//                        buffer = new byte[iS.available()];
//                    } catch (IOException e) {
//                        throw new RuntimeException(e);
//                    }
//                    //read the text file as a stream, into the buffer
//                    try {
//                        iS.read(buffer);
//                    } catch (IOException e) {
//                        throw new RuntimeException(e);
//                    }
//                    //create a output stream to write the buffer into
//                    ByteArrayOutputStream oS = new ByteArrayOutputStream();
//                    //write this buffer to the output stream
//                    try {
//                        oS.write(buffer);
//                    } catch (IOException e) {
//                        throw new RuntimeException(e);
//                    }
//                    //Close the Input and Output streams
//                    try {
//                        oS.close();
//                    } catch (IOException e) {
//                        throw new RuntimeException(e);
//                    }
//                    try {
//                        iS.close();
//                    } catch (IOException e) {
//                        throw new RuntimeException(e);
//                    }
//
//                    //return the output stream as a String
//                    String output = oS.toString();
//                    String[] numbers = output.split("\n");
//                    short[] shorts = new short[numbers.length];
//                    for(int j = 0; j<numbers.length; j++){
//                        String number = numbers[j].replace("\r", "");
//                        short shortNum = Short.parseShort(number);
//                        shorts[j] = shortNum;
//                    }
//                    return shorts;
//                }

//                short[] data = new short[4410*504];
//                for(int i=0; i<4410*504; i++){
//                    data[i]=100;
//                    if(i%4410==2200){
//                        data[i] = 15000;
//                    }
//                }
                return new short[10];
            }
        });

        // Popup for labeling the current room
        button_label_room.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Make a pop up asking for the label
                Intent intent = new Intent(MainActivity.this, LabelWindow.class);
                intent.putExtra("server_ip", server_ip);
                startActivity(intent);
            }
        });

        // Popup for getting top 5 and possibly labeling
        button_top_5.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {


                // TODO: get the top 5 room labels
                String[] room_labels= new String[5];
                room_labels[0] = "Room1";
                room_labels[1] = "Room2";
                room_labels[2] = "Room3";
                room_labels[3] = "Room4";
                room_labels[4] = "Room5";
                // Make a pop up showing the room labels
                Intent intent = new Intent(MainActivity.this, TopFiveWindow.class);
                intent.putExtra("room_labels", room_labels);
                startActivity(intent);
            }
        });
    }

    public TextView getRoomList() {
        return (TextView) findViewById(R.id.list_of_rooms);
    }
}