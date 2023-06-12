package com.example.myapplication;

import java.util.List;

public class Room {

    List<short[]> audio;
    String room_label;
    String building_label;

    List<WiFiFingerprint>  wifi_list;

    public Room(List<short[]> audio, String room, String building, List<WiFiFingerprint>  wifi_list){
        this.room_label = room;
        this.audio = audio;
        this.building_label = building;
        this.wifi_list = wifi_list;
    }
}
