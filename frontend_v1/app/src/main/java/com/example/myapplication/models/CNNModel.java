package com.example.myapplication.models;

import java.util.List;

public class CNNModel implements Model{
    @Override
    public void train(List<double[][]> trainX, List<Integer> trainY, List<double[][]> testX, List<Integer> testY) {

    }

    @Override
    public int predict(double[][] dataChunk) {
        return 0;
    }

    @Override
    public int evaluate(List<double[][]> testX, List<Integer> testY) {
        return 0;
    }
}
