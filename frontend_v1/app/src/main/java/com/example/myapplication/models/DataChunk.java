package com.example.myapplication.models;

public class DataChunk {
    float[][][][] spetrogram;

    private String building;

    private String label;

    public DataChunk(String building, String label) {
        this.building = building;
        this.label = label;
        this.spetrogram = new float[1][5][32][1];
    }

//    public void createSpectrogram(short[] data){
//        SpectrogramGenerator spectrogramGenerator = new SpectrogramGenerator(data, 256, 128);
//        float[][] result = spectrogramGenerator.getAbsoluteSpectrogramData();
//
//    }

    public float[][][][] getSpetrogram(){
        return this.spetrogram;
    }

    public void setSpetrogram(float[][][][] spetrogram) {
        this.spetrogram = spetrogram;
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
