package com.example.myapplication.RequestCallbacks;

import android.app.Activity;
import android.net.Uri;
import android.util.Log;

import com.example.myapplication.Globals;
import com.google.android.gms.net.CronetProviderInstaller;

import org.chromium.net.CronetEngine;
import org.chromium.net.UploadDataProvider;
import org.chromium.net.UploadDataProviders;
import org.chromium.net.UrlRequest;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.Arrays;
import java.util.List;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;

public class LabelCallback implements RecordingCallback {

    private String roomLabel;
    private String buildingLabel;

    public LabelCallback(String roomLabel, String buildingLabel) {
        this.buildingLabel = buildingLabel;
        this.roomLabel = roomLabel;
    }

    @Override
    public void run(Activity activity, List<float[]> data) {
        Log.i("BuildAndSendRequest", "Sending request");
        CronetProviderInstaller.installProvider(activity);
        CronetEngine.Builder myBuilder = new CronetEngine.Builder(activity);
        CronetEngine cronetEngine = myBuilder.build();

        Executor executor = Executors.newSingleThreadExecutor();
        String requestUrl = " http://"+ Globals.IP +":" + Globals.PORT +"/add_new_location_point";
        Uri.Builder uriBuilder = Uri.parse(requestUrl).buildUpon();
        uriBuilder.appendQueryParameter("placeLabel", this.roomLabel);
        uriBuilder.appendQueryParameter("buildingLabel", this.buildingLabel);
        String urlWithQueryParams = uriBuilder.build().toString();

        int count = 1;
        JSONObject jsonObject = new JSONObject();
        for(float[] array: data){
            try {
                jsonObject.put(String.valueOf(count), Arrays.toString(array));
            } catch (JSONException e) {

            }
            count++;
        }
        String requestBody = jsonObject.toString();

        UploadDataProvider uploadDataProvider = UploadDataProviders.create(requestBody.getBytes(), 0, requestBody.getBytes().length);

        UrlRequest.Builder requestBuilder = cronetEngine
                .newUrlRequestBuilder(
                        urlWithQueryParams, new MyUrlRequestCallback(), executor)
                .setHttpMethod("POST")
                .addHeader("Content-Type", "application/json")
                .setUploadDataProvider(uploadDataProvider, executor);

        UrlRequest request = requestBuilder.build();
        request.start();

        Log.i("BuildAndSendRequest", "request.start() executed");
    }
}
