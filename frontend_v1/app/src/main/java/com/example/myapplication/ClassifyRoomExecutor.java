package com.example.myapplication;

import android.content.Intent;

public class ClassifyRoomExecutor implements Runnable {

    private String ip;
    private MainActivity mainActivity;
    private String classifiedRoom;

    public ClassifyRoomExecutor(String ip, MainActivity mainActivity) {
        this.ip = ip;
        this.mainActivity = mainActivity;
        this.classifiedRoom = "NULL";
    }

    @Override
    public void run() {
        this.classifiedRoom = ServerCommunication.recognizeRoom(this.ip);

        System.out.println("RESULT:   " + this.classifiedRoom);

        this.mainActivity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                changeText();
            }
        });
    }

    private void changeText() {
        try {
            this.mainActivity.getClassifiedRoom().setText(this.classifiedRoom);
        } catch (Exception e) {
            System.out.println("TextView = null");
        }
        //Intent intent = new Intent(this.mainActivity, RecognizeWindow.class);
        //intent.putExtra("text", this.classifiedRoom);
    }
}
