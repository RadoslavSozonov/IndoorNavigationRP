package com.example.myapplication;

import java.util.List;

public class Room {

    String building_label;

    String room_label;
    List<short[]> audio;
    public Room(List<short[]> audio, String room, String building){
        this.room_label = room;
        this.audio = audio;
        this.building_label = building;
    }
}
