package com.example.myapplication;

public class WiFiInfo {
    String BSSID;
    String SSID;
    int level;

    public WiFiInfo(String BSSID, String SSID, int level) {
        this.BSSID = BSSID;
        this.SSID = SSID;
        this.level = level;
    }
}