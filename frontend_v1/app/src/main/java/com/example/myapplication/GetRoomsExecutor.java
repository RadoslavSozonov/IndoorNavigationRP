package com.example.myapplication;

import android.widget.TextView;

public class GetRoomsExecutor implements Runnable{

    String room_list;

    MainActivity mainActivity;

    String ip;

    public GetRoomsExecutor(String room_list, MainActivity mainActivity, String ip){
        this.room_list = room_list;
        this.mainActivity = mainActivity;
        this.ip = ip;
    }

    @Override
    public void run() {
        this.room_list = ServerCommunication.get_room_list(ip);
        this.mainActivity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                changeText();
            }
        });
    }

    private void changeText() {
        this.mainActivity.getRoomList().setText(this.room_list);
    }
}
