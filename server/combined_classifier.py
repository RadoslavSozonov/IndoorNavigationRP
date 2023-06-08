import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, accuracy_score
from utils import create_confusion_matrix

def weighted_average(acoustic_model, wifi_model, acoustic_weight, acoustic_sample, wifi_sample):
    prediction = acoustic_model.get_predictions(acoustic_sample)
    prediction_norm = ((prediction-np.min(prediction))/(np.max(prediction)-np.min(prediction)))[0]

    acoustic_prediction = np.asarray(prediction_norm)
    wifi_prediction = wifi_model.classify_probability(np.reshape(wifi_sample, (1,len(wifi_sample))))

    combined_probability = acoustic_weight * acoustic_prediction + wifi_prediction
    combined_prediction = np.argmax(combined_probability)
    
    return combined_prediction


def two_step(acoustic_model, wifi_model, top_k, acoustic_sample, wifi_sample):
    wifi_prediction = wifi_model.classify_probability(np.reshape(wifi_sample, (1,len(wifi_sample))))
    wifi_top = wifi_prediction.argsort()[-top_k:][::-1]
    
    prediction = acoustic_model.get_predictions(acoustic_sample)
    prediction_norm = ((prediction-np.min(prediction))/(np.max(prediction)-np.min(prediction)))[0]

    acoustic_prediction = np.asarray(prediction_norm)
    acoustic_top = acoustic_prediction.argsort()[:][::-1]

    for top_choice in acoustic_top:
        if np.any(wifi_top == top_choice):
            return top_choice

def wifi_top_k(wifi_model, top_k, wifi_sample):
    wifi_prediction = wifi_model.classify_probability(np.reshape(wifi_sample, (1,len(wifi_sample))))
    return wifi_prediction[0].argsort()[-top_k:][::-1]


def weighted_average_test_accuracy(acoustic_model, wifi_model, acoustic_weight, acoustic_test, wifi_test, labels):
    int_to_label = np.asarray(acoustic_model.get_int_to_label())
    combined_predictions = []
    for acoustic_sample, wifi_sample in zip(acoustic_test, wifi_test):
        combined_predictions.append(weighted_average(acoustic_model, wifi_model, acoustic_weight, acoustic_sample, wifi_sample))
    combined_predictions = np.asarray(combined_predictions)

    
    accuracy = accuracy_score(labels, combined_predictions)
    create_confusion_matrix(labels, combined_predictions, int_to_label, accuracy, "weighted_average")

    return accuracy

def two_step_test_accuracy(acoustic_model, wifi_model, top_k, acoustic_test, wifi_test, labels):
    int_to_label = np.asarray(acoustic_model.get_int_to_label())
    combined_predictions = []
    for acoustic_sample, wifi_sample in zip(acoustic_test, wifi_test):
        combined_predictions.append(two_step(acoustic_model, wifi_model, top_k, acoustic_sample, wifi_sample))

    accuracy = accuracy_score(labels, combined_predictions)
    create_confusion_matrix(labels, combined_predictions, int_to_label, accuracy, "two_step_localization")
    
    return accuracy

def wifi_top_k_test_accuracy(wifi_model, top_k, wifi_test, labels):
    int_to_label = wifi_model.get_int_to_label()
    wifi_top = []
    for wifi_sample in wifi_test:
        wifi_top.append(wifi_top_k(wifi_model, top_k, wifi_sample))
    combined_predictions = []
    for i, top_list in enumerate(wifi_top):
        if np.any(top_list == labels[i]):
            combined_predictions.append(labels[i])
        else:
            combined_predictions.append(top_list[0])
    accuracy = accuracy_score(labels, combined_predictions)

    create_confusion_matrix(labels, combined_predictions, int_to_label, accuracy, "top_k")
    
    return accuracy