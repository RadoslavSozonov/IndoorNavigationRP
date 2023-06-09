package com.example.myapplication.models;

public class DataChunk {
    double[][][][] spetrogram;

    private String building;

    private String label;

    public DataChunk(String building, String label) {
        this.building = building;
        this.label = label;
        this.spetrogram = new double[1][5][32][1];
    }

    public void createSpectrogram(short[] data){
        SpectrogramGenerator spectrogramGenerator = new SpectrogramGenerator(data, 256, 128);
        double[][] result = spectrogramGenerator.getAbsoluteSpectrogramData();

    }

    public double[][][][] getSpetrogram(){
        return this.spetrogram;
    }

    public void setSpetrogram(double[][][][] spetrogram) {
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
