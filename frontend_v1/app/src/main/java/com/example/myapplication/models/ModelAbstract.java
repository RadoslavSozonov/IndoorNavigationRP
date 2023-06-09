package com.example.myapplication.models;

import android.app.Activity;
import android.content.res.AssetFileDescriptor;
import android.util.Log;

import org.tensorflow.lite.Interpreter;

import java.io.FileInputStream;
import java.io.IOException;
import java.nio.MappedByteBuffer;
import java.nio.channels.FileChannel;

public abstract class ModelAbstract  implements Model{

    protected Interpreter tflite;

    public ModelAbstract(Activity activity, String modelName){
        try {
            this.tflite = new Interpreter(this.loadModelFile(activity, modelName));
        }catch (Exception ex){
            ex.printStackTrace();
        }
    }
    protected MappedByteBuffer loadModelFile(Activity activity, String model_name) {
        try {
            AssetFileDescriptor fileDescriptor=activity.getAssets().openFd(model_name);
            FileInputStream inputStream=new FileInputStream(fileDescriptor.getFileDescriptor());
            FileChannel fileChannel=inputStream.getChannel();
            long startOffset=fileDescriptor.getStartOffset();
            long declareLength=fileDescriptor.getDeclaredLength();
            return fileChannel.map(FileChannel.MapMode.READ_ONLY,startOffset,declareLength);
        } catch (Exception e){
            Log.i("ModelAbstract", e.getMessage());
            throw new RuntimeException(e);
        }

    }
}
