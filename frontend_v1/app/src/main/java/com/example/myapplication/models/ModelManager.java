package com.example.myapplication.models;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class ModelManager {
    private Model model;
    private DataSet dataSet;
    private List<Integer> labelsList;
    private Map<String, Integer> labelMap;

    public ModelManager(Model model, DataSet dataSet ) {
        this.model = model;
        List<String> labelList = dataSet.getDataset().stream().map(Data::getLabel).collect(Collectors.toList());
        this.dataSet = dataSet;
        this.labelMap = new HashMap<>();
        for(String label: labelList){
            labelMap.put(label, labelMap.size());
        }

    }

    public Model getModel() {
        return model;
    }

    public void setModel(Model model) {
        this.model = model;
    }

    public DataSet getDataSet() {
        return dataSet;
    }

    public void setDataSet(DataSet dataChunkList) {
        this.dataSet = dataChunkList;
    }

    public List<Integer> getLabelsList() {
        return labelsList;
    }

    public void setLabelsList(List<Integer> labelsList) {
        this.labelsList = labelsList;
    }

    public void trainModel(float trainingDataRatio){
        List<DataChunk> dataChunkList = dataSet.getDataset().stream().flatMap(x->x.getDataChunkList().stream()).collect(Collectors.toList());
        Collections.shuffle(dataChunkList);
        List<DataChunk> trainingSet = new ArrayList<>();
        List<DataChunk> testSet = new ArrayList<>();
        for(DataChunk dataChunk: dataChunkList){
            if(trainingSet.size()<=trainingDataRatio){
                trainingSet.add(dataChunk);
            } else {
                testSet.add(dataChunk);
            }
        }
        this.model.train(
                trainingSet.stream().map(DataChunk::getSpetrogram).collect(Collectors.toList()),
                trainingSet.stream().map(x->labelMap.get(x.getLabel())).collect(Collectors.toList()),
                testSet.stream().map(DataChunk::getSpetrogram).collect(Collectors.toList()),
                testSet.stream().map(x->labelMap.get(x.getLabel())).collect(Collectors.toList())
        );
    }

    public void evaluateModel(){
//        this.model.evaluate(dataChunkList, labelsList);
    }

    public int predict(DataChunk dataChunk){
        return model.predict(dataChunk.getSpetrogram());
    }

    public int predict(DataChunk dataChunk, String label){
        return model.predict(dataChunk.getSpetrogram());
    }
}
