package com.example.myapplication.RequestCallbacks;

import android.util.Log;

import org.chromium.net.CronetException;
import org.chromium.net.UrlRequest;
import org.chromium.net.UrlResponseInfo;

import java.nio.Buffer;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;

public class MyUrlRequestCallback extends UrlRequest.Callback {
    private static final String TAG = "MyUrlRequestCallback";
    private StringBuilder responseData = new StringBuilder();

    @Override
    public void onRedirectReceived(UrlRequest request, UrlResponseInfo info, String newLocationUrl) {
        Log.i(TAG, "onRedirectReceived method called.");
        // You should call the request.followRedirect() method to continue
        // processing the request.
        request.followRedirect();
    }

    @Override
    public void onResponseStarted(UrlRequest request, UrlResponseInfo info) {
        Log.i(TAG, "onResponseStarted method called.");
        ByteBuffer myBuffer = ByteBuffer.allocateDirect(102400);
        // You should call the request.read() method before the request can be
        // further processed. The following instruction provides a ByteBuffer object
        // with a capacity of 102400 bytes for the read() method. The same buffer
        // with data is passed to the onReadCompleted() method.
        int httpStatusCode = info.getHttpStatusCode();
        if (httpStatusCode == 200) {
            // The request was fulfilled. Start reading the response.
            request.read(myBuffer);
        } else if (httpStatusCode == 503) {
            // The service is unavailable. You should still check if the request
            // contains some data.
            request.read(myBuffer);
        }
//        responseHeaders = info.getAllHeaders();

    }

    @Override
    public void onReadCompleted(UrlRequest request, UrlResponseInfo info, ByteBuffer byteBuffer) {
        Log.i(TAG, "onReadCompleted method called.");
        // Convert ByteBuffer to String
        byteBuffer.flip();
        byte[] bytes = new byte[byteBuffer.remaining()];
        byteBuffer.get(bytes);
        String chunk = new String(bytes, StandardCharsets.UTF_8);

        // Append the current chunk to the response data
        responseData.append(chunk);
        // You should keep reading the request until there's no more data.
        byteBuffer.clear();
        request.read(byteBuffer);
    }

    @Override
    public void onSucceeded(UrlRequest request, UrlResponseInfo info) {
        Log.i(TAG, "onSucceeded method called.");
        String responseBody = responseData.toString();
        Log.i(TAG, responseBody);
    }

    @Override
    public void onFailed(UrlRequest request, UrlResponseInfo info, CronetException error) {
        // The request has failed. If possible, handle the error.
        Log.e(TAG, "The request failed.", error);
    }

    @Override
    public void onCanceled(UrlRequest request, UrlResponseInfo info) {
        // Free resources allocated to process this request.
    }

}
