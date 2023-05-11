package com.example.myapplication;

import com.google.gson.Gson;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.List;


public class ServerCommunication {
    public static String get_room_list() {
        URL url = null;

        try {
            url = new URL("http://192.168.50.77:5000/get_rooms");
        } catch (MalformedURLException e) {
            return "";
        }

        try {
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("GET");
            int status_code = connection.getResponseCode();
            if(status_code == HttpURLConnection.HTTP_OK) {
                BufferedReader in = new BufferedReader(new InputStreamReader(connection.getInputStream()));
                String inputLine;
                StringBuffer response = new StringBuffer();

                while ((inputLine = in.readLine()) != null) {
                    response.append(inputLine);
                }
                in.close();
                return response.toString();
            } else return "Server returned response: " + status_code;
        } catch (IOException e) {
            e.printStackTrace();
            return "Server error";
        }
    }

    public static void addRoom(Room room) {
        URL url = null;

        try {
            url = new URL("http://192.168.50.77:5000/add_room");
        } catch (MalformedURLException e) {
            return;
        }

        try {
            //String body = "{\"audio\": " + new Gson().toJson(audiolist) + "}";
            String body = new Gson().toJson(room);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("POST");
            connection.setRequestProperty("Content-Type", "application/json");
            connection.setDoOutput(true);
            connection.getOutputStream();
            DataOutputStream out = new DataOutputStream(connection.getOutputStream());
            out.writeBytes(body);
            connection.getResponseCode();

        } catch (IOException e) {
            e.printStackTrace();
            return;
        }


    }

}
