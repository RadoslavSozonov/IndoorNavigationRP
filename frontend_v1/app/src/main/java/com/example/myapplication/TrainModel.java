package com.example.myapplication;

import android.app.Activity;
import android.net.Uri;
import android.os.Bundle;
import android.util.DisplayMetrics;
import android.util.Log;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.TextView;

import com.example.myapplication.RequestCallbacks.MyUrlRequestCallback;
import com.google.android.gms.net.CronetProviderInstaller;

import org.chromium.net.CronetEngine;
import org.chromium.net.UrlRequest;
import org.json.JSONException;

import java.io.IOException;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;

public class TrainModel extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.train_model);

        TextView train_model_name = (TextView) findViewById(R.id.train_model);
        TextView building = (TextView) findViewById(R.id.building_name_train);
        TextView train_button = (Button) findViewById(R.id.train);

        train_button.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(View v) {
                String trainModelName = String.valueOf(train_model_name.getText());
                String buildingName = String.valueOf(building.getText());

                try {
                    if(trainModelName.length() > 0 && buildingName.length() > 0) {
                        trainModelRequest(buildingName, trainModelName);
                    }
                } catch (IOException e) {
                    throw new RuntimeException(e);
                } catch (JSONException e) {
                    throw new RuntimeException(e);
                }
            }
        });


        // Setup pop up layout
        DisplayMetrics displayMetrics = new DisplayMetrics();
        getWindowManager().getDefaultDisplay().getMetrics(displayMetrics);

        int width = displayMetrics.widthPixels;
        int height = displayMetrics.heightPixels;

        getWindow().setLayout((int) (width * 0.8), (int) (height * 0.8));

        WindowManager.LayoutParams layoutParams = getWindow().getAttributes();
        layoutParams.dimAmount = 0.35f;
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_DIM_BEHIND);
        getWindow().setAttributes(layoutParams);


        // Make a back button
        Button button_back = (Button) findViewById(R.id.button_back_train_window);
        button_back.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });
    }

    private void trainModelRequest(String buildingName, String modelName) throws IOException, JSONException {
        Log.i("BuildAndSendRequest", "Sending request");
        CronetProviderInstaller.installProvider(this);
        CronetEngine.Builder myBuilder = new CronetEngine.Builder(this);
        CronetEngine cronetEngine = myBuilder.build();

        Executor executor = Executors.newSingleThreadExecutor();
        String requestUrl = " http://192.168.56.1:5000/train_model_for_building";
        Uri.Builder uriBuilder = Uri.parse(requestUrl).buildUpon();
        uriBuilder.appendQueryParameter("buildingLabel", buildingName);
        uriBuilder.appendQueryParameter("modelToTrain", modelName);
        String urlWithQueryParams = uriBuilder.build().toString();

        UrlRequest.Builder requestBuilder = cronetEngine
                .newUrlRequestBuilder(
                        urlWithQueryParams, new MyUrlRequestCallback(), executor
                );

        UrlRequest request = requestBuilder.build();
        request.start();

        Log.i("BuildAndSendRequest", "request.start() executed");
    }
}
