package com.example.myapplication;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;


public class ServerCommunication {
    public static String get_room_list() {
        URL url = null;

        try {
            url = new URL("http://192.168.2.17:5000/get_rooms");
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

}
