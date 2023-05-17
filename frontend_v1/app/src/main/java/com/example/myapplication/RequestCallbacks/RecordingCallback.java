package com.example.myapplication.RequestCallbacks;

import android.app.Activity;

import java.util.List;

public interface RecordingCallback {

    public void run(Activity activity, List<short[]> data);

}
