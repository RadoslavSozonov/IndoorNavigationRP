package com.example.myapplication.models;

import java.util.ArrayList;
import java.util.List;

public class Data {
    private List<DataChunk> dataChunkList;
    private String building;
    private String label;


    public Data(String building, String label) {
        this.dataChunkList = new ArrayList<>();
        this.building = building;
        this.label = label;
    }

    public void addData(short[] audioData){
        int offset = findOffset(audioData);
        int intervalsToOmit = 2;
        int intervalDataPoints = 4410;
        int audioIntervals = audioData.length/intervalDataPoints;

        for(int i = intervalsToOmit; i<audioIntervals-intervalsToOmit; i++){
            short[] chunk = new short[intervalDataPoints];
            for(int y = 0; y<intervalDataPoints; y++){
                chunk[y] = audioData[i*intervalDataPoints+y+offset];
            }
            DataChunk dataChunk = new DataChunk();
            dataChunk.createSpectrogram(chunk);
            dataChunkList.add(dataChunk);
        }

    }

    public int findOffset(short[] audioData){
        for(int i = 0; i< audioData.length;i++){
            if(audioData[i]>10000){
                return i-50;
            }
        }
        return 0;
    }

    public List<DataChunk> getDataChunkList() {
        return dataChunkList;
    }

    public void setDataChunkList(List<DataChunk> dataChunkList) {
        this.dataChunkList = dataChunkList;
    }

    public String getBuilding() {
        return building;
    }

    public void setBuilding(String building) {
        this.building = building;
    }

    public String getLabel() {
        return label;
    }

    public void setLabel(String label) {
        this.label = label;
    }
}
