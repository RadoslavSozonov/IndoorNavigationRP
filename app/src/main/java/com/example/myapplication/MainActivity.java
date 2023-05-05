package com.example.myapplication;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import org.w3c.dom.Text;

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Components of the layout
        Button button_recognize = (Button) findViewById(R.id.button_recognize);
        Button button_label_room = (Button) findViewById(R.id.button_label_room);
        Button button_top_5 = (Button) findViewById(R.id.button_top_5);
        TextView list_of_rooms = (TextView) findViewById(R.id.list_of_rooms);

        // Code for recognizing the current room
        button_recognize.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // TODO: ADD CODE FOR CLASSIFYING ROOM HERE

                String room_label = "room label";

                // Make a pop up showing the room label
                Intent intent = new Intent(MainActivity.this, Pop.class);
                intent.putExtra("title", "The room label is:");
                intent.putExtra("text", room_label);
                startActivity(intent);
            }
        });

        // Code for labeling the current room
        button_label_room.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Make a pop up showing the room label
                Intent intent = new Intent(MainActivity.this, LabelWindow.class);

                startActivity(intent);
            }
        });
    }
}