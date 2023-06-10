package com.example.myapplication.models;

import java.util.List;

public interface ModelInterface {
    public void train(List<float[][][][]> trainX, List<Integer> trainY, List<float[][][][]> testX, List<Integer> testY);
    public int predict(float[][][][] dataChunk);
    public float evaluate(List<float[][][][]> testX, List<Integer> testY);
}
