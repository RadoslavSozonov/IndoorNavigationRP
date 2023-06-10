package com.example.myapplication.models;

import java.util.ArrayList;
import java.util.List;

public class DataSet {
    private List<Data> dataset;

    private String building;

    public DataSet(String building) {
        this.building = building;
        this.dataset = new ArrayList<>();
    }

    public String getBuilding() {
        return building;
    }

    public void setBuilding(String building) {
        this.building = building;
    }

    public List<Data> getDataset() {
        return dataset;
    }

    public boolean addData(Data data){
        return dataset.add(data);
    }

    public int dataChunksSize(){
        return dataset.stream().map(Data::getSize).reduce(0, Integer::sum);
    }
    public void setDataset(List<Data> dataset) {
        this.dataset = dataset;
    }
}
