package com.example.myapplication.models;

import java.util.ArrayList;
import java.util.List;

public class DataSet {
    private List<Data> dataset;

    public DataSet() {
        this.dataset = new ArrayList<>();
    }

    public List<Data> getDataset() {
        return dataset;
    }

    public boolean addData(Data data){
        return dataset.add(data);
    }

    public void setDataset(List<Data> dataset) {
        this.dataset = dataset;
    }
}
