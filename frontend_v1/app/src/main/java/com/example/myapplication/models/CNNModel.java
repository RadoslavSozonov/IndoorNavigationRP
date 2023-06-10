package com.example.myapplication.models;

import android.app.Activity;

import java.util.List;
import org.tensorflow.lite.support.tensorbuffer.TensorBuffer;

public class CNNModel {

//    public CNNModel(Activity activity, String modelName){
//        super(activity, modelName);
//    }
//    @Override
//    public void train(List<float[][][][]> trainX, List<Integer> trainY, List<float[][][][]> testX, List<Integer> testY) {
//
//    }
//
//    @Override
//    public int predict(float[][][][] dataChunk) {
////        float[][] results = new float[1][5];
//        int[] inputShape = super.tflite.getInputTensor(0).shape();
////        System.out.println(super.tflite.getInputTensor(0).dataType());
//        int[] outputShape = super.tflite.getOutputTensor(0).shape();
////        System.out.println(super.tflite.getOutputTensor(0).dataType());
//
//        TensorBuffer input = TensorBuffer.createFixedSize(
//                inputShape,
//                super.tflite.getInputTensor(0).dataType()
//        );
//        TensorBuffer output = TensorBuffer.createFixedSize(
//                outputShape,
//                super.tflite.getOutputTensor(0).dataType()
//        );
//        float[] flatDataChunk = new float[32*5];
//        for(int i = 0; i < dataChunk.length; i++){
//            for(int y = 0; y < dataChunk[0].length; y++){
//                flatDataChunk[i* dataChunk.length+y] = dataChunk[0][i][y][0];
//            }
//        }
//
//        input.loadArray(flatDataChunk, inputShape);
////        output.loadArray(results, outputShape);
//
//        super.tflite.run(input.getBuffer(), output.getBuffer());
//        float[] results = output.getFloatArray();
//        int maxIndex = 0;
//        float value = 0;
//        for(int i = 0; i<5;i++){
//            if(results[i] > value){
//                maxIndex=i;
//            }
//        }
//        return maxIndex;
//    }
//
//    @Override
//    public float evaluate(List<float[][][][]> testX, List<Integer> testY) {
//        int truePredicted = 0;
//        int predictions = 0;
//        for(float[][][][] data: testX){
//            if(this.predict(data) == testY.get(predictions)){
//                truePredicted+=1;
//            }
//            predictions+=1;
//        }
//        return truePredicted/predictions;
//    }
}
