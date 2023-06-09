package com.example.myapplication.models;

import android.app.Activity;

import org.tensorflow.lite.Interpreter;

import java.util.List;

public class CNNModel extends ModelAbstract implements Model{

    public CNNModel(Activity activity, String modelName){
        super(activity, modelName);
    }
    @Override
    public void train(List<double[][][][]> trainX, List<Integer> trainY, List<double[][][][]> testX, List<Integer> testY) {

    }

    @Override
    public int predict(double[][][][] dataChunk) {
        float[][] output=new float[1][1];
        super.tflite.run(dataChunk, output);
        return Math.round(output[0][0]);
    }

    @Override
    public float evaluate(List<double[][][][]> testX, List<Integer> testY) {
        int truePredicted = 0;
        int predictions = 0;
        for(double[][][][] data: testX){
            if(this.predict(data) == testY.get(predictions)){
                truePredicted+=1;
            }
            predictions+=1;
        }
        return truePredicted/predictions;
    }
}
