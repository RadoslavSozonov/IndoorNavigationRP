package com.example.myapplication.models;

import android.app.Activity;
import android.content.res.AssetFileDescriptor;
import android.util.Log;

import org.tensorflow.lite.Interpreter;
import org.tensorflow.lite.support.tensorbuffer.TensorBuffer;

import java.io.FileInputStream;
import java.nio.MappedByteBuffer;
import java.nio.channels.FileChannel;
import java.util.List;

public class Model implements ModelInterface {

    protected Interpreter tflite;

    public Model(Activity activity, String modelName){
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

    @Override
    public void train(List<float[][][][]> trainX, List<Integer> trainY, List<float[][][][]> testX, List<Integer> testY) {

    }

    @Override
    public int predict(float[][][][] dataChunk) {
        //        float[][] results = new float[1][5];
        int[] inputShape = this.tflite.getInputTensor(0).shape();
//        System.out.println(super.tflite.getInputTensor(0).dataType());
        int[] outputShape = this.tflite.getOutputTensor(0).shape();
//        System.out.println(super.tflite.getOutputTensor(0).dataType());

        TensorBuffer input = TensorBuffer.createFixedSize(
                inputShape,
                this.tflite.getInputTensor(0).dataType()
        );
        TensorBuffer output = TensorBuffer.createFixedSize(
                outputShape,
                this.tflite.getOutputTensor(0).dataType()
        );
        float[] flatDataChunk = new float[32*5];
        for(int i = 0; i < dataChunk.length; i++){
            for(int y = 0; y < dataChunk[0].length; y++){
                flatDataChunk[i* dataChunk.length+y] = dataChunk[0][i][y][0];
            }
        }

        input.loadArray(flatDataChunk, inputShape);
//        output.loadArray(results, outputShape);

        this.tflite.run(input.getBuffer(), output.getBuffer());
        float[] results = output.getFloatArray();
        int maxIndex = 0;
        float value = 0;
        for(int i = 0; i<5;i++){
            if(results[i] > value){
                maxIndex=i;
            }
        }
        return maxIndex;
    }

    @Override
    public float evaluate(List<float[][][][]> testX, List<Integer> testY) {
        int truePredicted = 0;
        int predictions = 0;
        for(float[][][][] data: testX){
            if(this.predict(data) == testY.get(predictions)){
                truePredicted+=1;
            }
            predictions+=1;
        }
        return (float) truePredicted/predictions;
    }
}
