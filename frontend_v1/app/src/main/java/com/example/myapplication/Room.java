package com.example.myapplication;

import java.util.List;

public class Room {
    List<short[]> audio;
    String room_label;
    String building_label;
    Boolean passive;
    int amount;
    double interval;
    public Room(List<short[]> audio, String room, String building, Boolean passive, int amount, double interval){
        this.room_label = room;
        this.audio = audio;
        this.building_label = building;
        this.passive = passive;
        this.amount = amount;
        this.interval = interval;
    }
}
