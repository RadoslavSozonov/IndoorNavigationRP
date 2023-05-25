package com.example.myapplication;

import android.app.Activity;
import android.net.Uri;
import android.util.Log;

import com.example.myapplication.RequestCallbacks.MyUrlRequestCallback;
import com.google.android.gms.net.CronetProviderInstaller;

import org.chromium.net.CronetEngine;
import org.chromium.net.UploadDataProvider;
import org.chromium.net.UploadDataProviders;
import org.chromium.net.UrlRequest;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;

public class ServerCommunicationCronetEngine {

    public static void addNewPlace(List<short[]> audio, String buildingLabel, String roomLabel, String ip, Activity activity) {
        UrlRequest request = null;
        try {
            request = buildRequest(audio, buildingLabel, roomLabel, ip, activity);
            request.start();
            Log.i("BuildAndSendRequest", "request.start() executed");
        } catch (IOException e) {
            throw new RuntimeException(e);
        } catch (JSONException e) {
            throw new RuntimeException(e);
        }
    }

    private static UrlRequest buildRequest(List<short[]> audio, String buildingLabel, String roomLabel, String ip, Activity activity) throws IOException, JSONException {
        Log.i("BuildAndSendRequest", "Sending request");
        CronetProviderInstaller.installProvider(activity);
        CronetEngine.Builder myBuilder = new CronetEngine.Builder(activity);
        CronetEngine cronetEngine = myBuilder.build();

        Executor executor = Executors.newSingleThreadExecutor();
        String requestUrl = "http://"+ip+":5000/add_new_location_point";
        Uri.Builder uriBuilder = Uri.parse(requestUrl).buildUpon();
        uriBuilder.appendQueryParameter("placeLabel", roomLabel);
        uriBuilder.appendQueryParameter("buildingLabel", buildingLabel);
        String urlWithQueryParams = uriBuilder.build().toString();

        int count = 1;
        JSONObject jsonObject = new JSONObject();
        for(short[] array: audio){
            System.out.println(Arrays.toString(array));
            jsonObject.put(String.valueOf(count), Arrays.toString(array));
            count++;
        }
        String requestBody = jsonObject.toString();

        UploadDataProvider uploadDataProvider = UploadDataProviders.create(requestBody.getBytes(), 0, requestBody.getBytes().length);

        UrlRequest.Builder requestBuilder = cronetEngine
                .newUrlRequestBuilder(
                        urlWithQueryParams,
                        new MyUrlRequestCallback(),
                        executor
                )
                .setHttpMethod("POST")
                .addHeader("Content-Type", "application/json")
                .setUploadDataProvider(uploadDataProvider, executor);

        UrlRequest request = requestBuilder.build();

        return request;
    }
}
