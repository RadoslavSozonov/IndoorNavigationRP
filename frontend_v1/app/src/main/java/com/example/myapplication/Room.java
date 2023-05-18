package com.example.myapplication;

import java.util.List;

public class Room {
    List<short[]> audio;
    String room_label;
    String building_label;
    public Room(List<short[]> audio, String room, String building){
        this.room_label = room;
        this.audio = audio;
        this.building_label = building;
    }
}
