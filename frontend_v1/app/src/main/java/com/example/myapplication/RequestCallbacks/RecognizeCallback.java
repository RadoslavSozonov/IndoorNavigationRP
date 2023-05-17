package com.example.myapplication.RequestCallbacks;

import android.app.Activity;
import android.net.Uri;
import android.util.Log;

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

public class RecognizeCallback implements RecordingCallback {

    @Override
    public void run(Activity activity, List<short[]> recordingData) {
        Log.i("ClassifySendRequest", "Sending request");
        CronetProviderInstaller.installProvider(activity);
        CronetEngine.Builder myBuilder = new CronetEngine.Builder(activity);
        CronetEngine cronetEngine = myBuilder.build();

        Executor executor = Executors.newSingleThreadExecutor();
        String requestUrl = " http://192.168.56.1:5000/classify";
        Uri.Builder uriBuilder = Uri.parse(requestUrl).buildUpon();
        String urlWithQueryParams = uriBuilder.build().toString();

        JSONObject jsonObject = new JSONObject();

        try {
            jsonObject.put("recording", Arrays.toString(recordingData.get(0)));
        } catch (JSONException e) {

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

        Log.i("ClassifySendRequest", "request.start() executed");
    }
}
