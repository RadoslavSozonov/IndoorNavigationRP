package com.example.myapplication;

import android.widget.TextView;

public class GetRoomsExecutor implements Runnable{

    String room_list;

    MainActivity mainActivity;

    public GetRoomsExecutor(String room_list, MainActivity mainActivity){
        this.room_list = room_list;
        this.mainActivity = mainActivity;
    }

    @Override
    public void run() {
        this.room_list = ServerCommunication.get_room_list();
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
