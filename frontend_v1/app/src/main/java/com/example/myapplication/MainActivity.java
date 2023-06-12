package com.example.myapplication;

import androidx.activity.result.ActivityResult;
import androidx.activity.result.ActivityResultCallback;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AppCompatActivity;
import android.os.BatteryManager;
import android.content.Context;

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
import com.example.myapplication.models.DataChunk;
import com.example.myapplication.models.DataSet;
import com.example.myapplication.models.Model;
import com.example.myapplication.models.ModelManager;

import java.io.BufferedReader;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.lang.reflect.Field;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.time.Instant;
import java.time.ZonedDateTime;
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
                String[] modelNames = new String[]{
                        "cnn_conv_16_32_dense_1024_2023_06_09_16_27_EWI7_06.tflite",
                        "cnn_conv_32_32_dense_1024_2023_06_09_16_30_EWI7_06.tflite",
                        "cnn_conv_32_64_128_dense_512_2023_06_09_16_40_EWI7_06.tflite",
                        "cnn_conv_128_64_64_dense_1024_2023_06_09_16_33_EWI7_06.tflite",
                        "cnn_conv_256_128_dense_1024_2023_06_09_16_45_EWI7_06.tflite",
                        "cnn_conv_512_128_dense_512_2023_06_09_17_08_EWI7_06.tflite",
                        "dnn_dense_256_512_256_2023_06_09_17_43_EWI7_06.tflite",
                        "dnn_dense_256_512_1024_2023_06_09_17_49_EWI7_06.tflite",
                        "dnn_dense_512_128_2048_512_2023_06_09_17_56_EWI7_06.tflite",
                        "dnn_dense_512_256_256_64_2023_06_09_17_41_EWI7_06.tflite",
                        "dnn_dense_1024_512_2023_06_09_17_45_EWI7_06.tflite",
                        "dnn_dense_4096_16_2023_06_09_17_52_EWI7_06.tflite",
                        "rnn_lstm_32_64_dense_1024_2023_06_11_09_42_EWI7_06.tflite",
                        "rnn_lstm_64_64_dense_256_2023_06_11_09_35_EWI7_06.tflite",
                        "rnn_lstm_64_128_dense_1024_2023_06_11_09_45_EWI7_06.tflite",
                        "rnn_lstm_64_dense_1024_2023_06_11_09_40_EWI7_06.tflite",
                        "rnn_lstm_128_dense_128_2023_06_11_09_38_EWI7_06.tflite",
                        "rnn_lstm_256_128_dense_256_2023_06_11_09_49_EWI7_06.tflite"
                };
                BatteryManager mBatteryManager =
                        (BatteryManager)activity.getSystemService(Context.BATTERY_SERVICE);

                for(String modelName: modelNames){
                    Model model = new Model(activity, modelName);
                    ModelManager modelManager = new ModelManager(model, dataSet);
                    int dataChunksSize = dataSet.dataChunksSize();
                    if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
                        long startEnergy = mBatteryManager.getLongProperty(BatteryManager.BATTERY_PROPERTY_ENERGY_COUNTER);
                        long startTime = ZonedDateTime.now().toInstant().toEpochMilli();
                        float acc = modelManager.evaluateModel();
                        long endTime = ZonedDateTime.now().toInstant().toEpochMilli();
                        long endEnergy = mBatteryManager.getLongProperty(BatteryManager.BATTERY_PROPERTY_ENERGY_COUNTER);
                        float averageDuration = (float) (endTime - startTime)/dataChunksSize;
                        float averageEnergy = (float) (endEnergy-startEnergy)/dataChunksSize;
                        String input = modelName+" "
                                + acc +" "
                                + Math.round(averageDuration*100)/100 +"ms "
                                + Math.round(averageEnergy*100)/100 +"nWh\n";
                        Log.i("MODEL RESULTS", input);
                        OutputStreamWriter outputStreamWriter = null;
                        try {
                            outputStreamWriter = new OutputStreamWriter(activity.openFileOutput(dataSet.getBuilding()+".txt", Context.MODE_PRIVATE));
                            outputStreamWriter.write(input);
                        }
                        catch (IOException e) {
                            Log.e("Exception", "File write failed: " + e.toString());
                        }
                        finally {
                            try {
                                outputStreamWriter.close();
                                System.out.println(activity.getFilesDir().getAbsolutePath());
                            } catch (IOException e) {
                                throw new RuntimeException(e);
                            }
                        }
                    }

                }



            }

            public DataSet loadAudioData(){
//                InputStream inputStream = new

                Resources resources = getResources();
                InputStream iS;
                Field[] fields=R.raw.class.getFields();

                DataSet dataList = new DataSet("ewi9_06");
                for(int i = 0; i<fields.length;i++){

                    String[] split = fields[i].getName().split("_");
                    String buildingName = split[0]+"_"+split[1];

                    if(!buildingName.contains("ewi9_06")){
                        continue;
                    }

                    String label = fields[i].getName().split("_")[2].split("\\.")[0];
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
                    Data data = new Data("Ewi", label);
                    String[] specrograms = output.split("B");
                    for(String specrogram: specrograms){
                        if(specrogram.length()<10){
                            break;
                        }
                        String[] rows = specrogram.split("A");
                        int n = 0;
                        float[][][][] spectr = new float[1][5][32][1];
                        for(String row: rows){
                            int m = 0;
                            String[] numbers = row.split("\r\n");
                            if(numbers.length == 0 || numbers.length == 1){
                                break;
                            }
                            for(String number: numbers){
                                if(number.length() == 0) {
                                    break;
                                }
                                float shortNum = Float.parseFloat(number);
                                spectr[0][n][m][0] = shortNum;
                                m++;
                            }
                            n++;
                        }
                        DataChunk dataChunk = new DataChunk(buildingName, label);
                        dataChunk.setSpetrogram(spectr);
                        data.getDataChunkList().add(dataChunk);
                    }

                    dataList.addData(data);

                }

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