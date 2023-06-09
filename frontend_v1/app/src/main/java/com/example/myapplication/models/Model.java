package com.example.myapplication.models;

import java.util.List;

public interface Model {
    public void train(List<double[][][][]> trainX, List<Integer> trainY, List<double[][][][]> testX, List<Integer> testY);
    public int predict(double[][][][] dataChunk);
    public float evaluate(List<double[][][][]> testX, List<Integer> testY);
}
