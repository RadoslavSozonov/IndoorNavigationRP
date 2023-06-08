package com.example.myapplication.models;

public class DataChunk {
    double[][] spetrogram;

    private String building;

    private String label;

    public DataChunk() {
        this.spetrogram = new double[5][32];
    }

    public void createSpectrogram(short[] data){
        SpectrogramGenerator spectrogramGenerator = new SpectrogramGenerator(data, 256, 128);
        double[][] result = spectrogramGenerator.getNormalizedSpectrogramData();

    }

    public double[][] getSpetrogram(){
        return this.spetrogram;
    }

    public void setSpetrogram(double[][] spetrogram) {
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
