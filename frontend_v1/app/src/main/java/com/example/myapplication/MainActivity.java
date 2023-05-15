package com.example.myapplication;

import androidx.activity.result.ActivityResultCallback;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

public class MainActivity extends AppCompatActivity {
    private String rooms = "";
    private String server_ip = "";
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Components of the layout
        Button button_recognize = (Button) findViewById(R.id.button_recognize);
        Button button_label_room = (Button) findViewById(R.id.button_label_room);
        Button button_top_5 = (Button) findViewById(R.id.button_top_5);
        TextView list_of_rooms = (TextView) findViewById(R.id.list_of_rooms);

        list_of_rooms.setText(rooms);


        // Make a pop up showing the room label
        Intent server_ip_intent = new Intent(MainActivity.this, SetServerIp.class);

        ActivityResultLauncher<Intent> serverActivityIpLauncher =
                registerForActivityResult(new
                                ActivityResultContracts.StartActivityForResult(),
                        (result) -> {
                            server_ip = result.getData().getStringExtra("server_ip");

                            new Thread(new GetRoomsExecutor(rooms, this, server_ip)).start();
                            // code to process data from activity called
                        }
                );

        serverActivityIpLauncher.launch(server_ip_intent);
        // Popup for recognizing the current room
        button_recognize.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // TODO: get the label of the room
                String room_label = "room 1";


                // Make a pop up showing the room label
                Intent intent = new Intent(MainActivity.this, RecognizeWindow.class);
                intent.putExtra("title", "The room label is:");
                intent.putExtra("text", room_label);
                startActivity(intent);
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