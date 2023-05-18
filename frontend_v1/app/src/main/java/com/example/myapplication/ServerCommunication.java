package com.example.myapplication;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.lang.reflect.Type;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.Arrays;
import java.util.List;
import java.util.Map;



public class ServerCommunication {
    public static String get_room_list(String ip) {
        URL url = null;

        try {
            url = new URL("http://" + ip +":5000/get_rooms");
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
                String json_string = response.toString();
                Type building_map_type = new TypeToken<Map<String, String[]>>() {}.getType();
                Map<String, String[]> rooms = new Gson().fromJson(json_string, building_map_type);

                String final_list = "";
                for(Map.Entry<String, String[]> entry: rooms.entrySet()) {
                    final_list += entry.getKey() + ": " + Arrays.toString(entry.getValue()) + "\n";
                }
                return final_list;
            } else return "Server returned response: " + status_code;
        } catch (IOException e) {
            e.printStackTrace();
            return "Server error";
        }
    }

    public static void addRoom(Room room, String ip) {
        URL url = null;

        try {
            url = new URL("http://" + ip +":5000/add_room");
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
