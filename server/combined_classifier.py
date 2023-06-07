import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, accuracy_score
from utils import create_confusion_matrix

def weighted_average(acoustic_model, wifi_model, acoustic_test, wifi_test, labels):
    int_to_label = np.asarray(acoustic_model.get_int_to_label())
    acoustic_predictions = []
    for i, acoustic_sample in enumerate(acoustic_test):
        x = acoustic_model.get_predictions(acoustic_sample)
        x_norm = (x-np.min(x))/(np.max(x)-np.min(x))
        acoustic_predictions.append(x_norm[0])
    acoustic_predictions = np.asarray(acoustic_predictions)
    wifi_predictions = wifi_model.classify_probability(wifi_test)

    


    combined_probability = 0.3 * acoustic_predictions + wifi_predictions
    combined_predictions = np.argmax(combined_probability, axis=1)
    
    create_confusion_matrix(labels, combined_predictions, int_to_label, "./metadata/accuracy/weighted_average_confusion_matrix.png")

    accuracy = accuracy_score(labels, combined_predictions)
    return accuracy

def two_step_localization(acoustic_model, wifi_model, acoustic_test, wifi_test, labels):
    int_to_label = np.asarray(acoustic_model.get_int_to_label())
    wifi_predictions = wifi_model.classify_probability(wifi_test)
    wifi_top = []
    for i, wifi in enumerate(wifi_predictions):
        wifi_top.append(wifi.argsort()[-5:][::-1])
    
    acoustic_predictions = []
    for i, acoustic_sample in enumerate(acoustic_test):
        x = acoustic_model.get_predictions(acoustic_sample)
        x_norm = (x-np.min(x))/(np.max(x)-np.min(x))
        acoustic_predictions.append(x_norm[0])
    acoustic_predictions = np.asarray(acoustic_predictions)

    combined_predictions = []
    for i, top_list in enumerate(wifi_top):
        acoustic_top = acoustic_predictions[i].argsort()[:][::-1]
        for top_choice in acoustic_top:
            if np.any(top_list == top_choice):
                combined_predictions.append(top_choice)
                break

    create_confusion_matrix(labels, combined_predictions, int_to_label, "./metadata/accuracy/two_step_confusion_matrix.png")
    
    accuracy = accuracy_score(labels, combined_predictions)
    return accuracy