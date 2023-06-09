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

import com.example.myapplication.models.CNNModel;
import com.example.myapplication.models.Data;
import com.example.myapplication.models.DataSet;
import com.example.myapplication.models.ModelAbstract;
import com.example.myapplication.models.ModelManager;

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
    private String server_ip = "145.94.211.247";

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
                DataSet dataSet = loadAudioData();
                System.out.println("Data collected");
                String modelName = "cnn_conv_16_32_dense_1024_2023_06_09_16_27_EWI7_06.tflite";
                ModelAbstract model = new CNNModel(activity, modelName);
                ModelManager modelManager = new ModelManager(model, dataSet);
                modelManager.evaluateModel();
            }

            public DataSet loadAudioData(){
//                InputStream inputStream = new
                DataSet dataList = new DataSet();
                Resources resources = getResources();
                InputStream iS;
                Field[] fields=R.raw.class.getFields();
                for(int i = 0; i<fields.length;i++){
                    String modelName = fields[i].getName().split("_")[2].split("\\.")[0];
                    System.out.println();
                    int rID = 0;
                    try {
                        rID = fields[i].getInt(fields[i]);
                    } catch (IllegalAccessException e) {
                        throw new RuntimeException(e);
                    }
                    //get the file as a stream
                    iS = resources.openRawResource(rID);

                    //create a buffer that has the same size as the InputStream
                    byte[] buffer = new byte[0];
                    //create a output stream to write the buffer into
                    ByteArrayOutputStream oS = new ByteArrayOutputStream();
                    try {
                        buffer = new byte[iS.available()];

                        //read the text file as a stream, into the buffer
                        iS.read(buffer);
                        //write this buffer to the output stream
                        oS.write(buffer);
                        oS.close();
                        iS.close();
                    } catch (IOException e) {
                        throw new RuntimeException(e);
                    }

                    //return the output stream as a String
                    String output = oS.toString();
                    String[] numbers = output.substring(0, 100*4410).split("\n");
                    short[] shorts = new short[numbers.length];
                    Log.i("Label", modelName);
                    for(int j = 0; j<numbers.length; j++){
                        String number = numbers[j].replace("\r", "");
                        short shortNum = Short.parseShort(number);
                        shorts[j] = shortNum;
                    }
                    Data data = new Data("Ewi", modelName);
                    data.addData(shorts);
                    dataList.addData(data);

                }

//                short[] data = new short[4410*504];
//                for(int i=0; i<4410*504; i++){
//                    data[i]=100;
//                    if(i%4410==2200){
//                        data[i] = 15000;
//                    }
//                }
                return dataList;
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