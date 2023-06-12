import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, accuracy_score
from utils import create_confusion_matrix
from threading import Lock

class WeightedAverage:
    def __init__(self, acoustic_model, wifi_model, int_to_label):
        self.int_to_label = int_to_label
        self.acoustic_model = acoustic_model
        self.wifi_model = wifi_model
        self.training_lock = Lock()
        self.model_trained = False
        self.weight = -1
    
    def set_int_to_label(self,int_to_label):
        self.int_to_label = int_to_label

    def train(self, acoustic_training_dataset, wifi_training_dataset, acoustic_test_dataset, wifi_test_dataset):
        with self.training_lock:
            acoustic_train_set, acoustic_train_label = acoustic_training_dataset
            acoustic_test_set, acoustic_test_label = acoustic_test_dataset
            wifi_train_set, wifi_train_label = wifi_training_dataset
            wifi_test_set, wifi_test_label = wifi_test_dataset

            best_weight = 0.5
            best_accuracy = "NAN"
            # best_weight = -1
            # best_accuracy = -1
            # for weight in np.arange(0, 5, 0.1):
            #     accuracy = self.weighted_average_test_accuracy(acoustic_train_set, wifi_train_set, wifi_train_label, weight, False)
            #     if best_accuracy < accuracy:
            #         best_weight = weight
            #         best_accuracy = accuracy
            
            test_accuracy = self.weighted_average_test_accuracy(acoustic_test_set, wifi_test_set, wifi_test_label, best_weight, True)
            print("BEST WEIGHT:" + str(best_weight) + " TRAIN_ACCURACY:" + str(best_accuracy) + " TEST_ACCURACY:" + str(test_accuracy))
            self.weight = best_weight
            self.model_trained = True
            return test_accuracy

    def get_prediction(self, acoustic_sample, wifi_sample, acoustic_weight=None):
        if acoustic_weight == None:
            acoustic_weight = self.weight
        acoustic_prediction = self.acoustic_model.get_predictions(acoustic_sample)[0]
        wifi_prediction = self.wifi_model.classify_probability(np.reshape(wifi_sample, (1,len(wifi_sample))))[0]

        combined_probability = acoustic_weight * acoustic_prediction + wifi_prediction
        combined_prediction = np.argmax(combined_probability)
        
        return combined_prediction

    def classify(self, acoustic_sample, wifi_sample):
        return self.int_to_label[self.get_prediction(acoustic_sample, wifi_sample)]

    def weighted_average_test_accuracy(self, acoustic_test, wifi_test, labels, acoustic_weight, save_matrix):
        combined_predictions = []
        for acoustic_sample, wifi_sample in zip(acoustic_test, wifi_test):
            combined_predictions.append(self.get_prediction(acoustic_sample, wifi_sample, acoustic_weight))
        combined_predictions = np.asarray(combined_predictions)

        accuracy = accuracy_score(labels, combined_predictions)
        if save_matrix:
            create_confusion_matrix(labels, combined_predictions, self.int_to_label, accuracy, "weighted_average_weight_" + str(self.weight))

        return accuracy


class TwoStep:
    def __init__(self, acoustic_model, wifi_model, int_to_label):
        self.int_to_label = int_to_label
        self.acoustic_model = acoustic_model
        self.wifi_model = wifi_model
        self.training_lock = Lock()
        self.model_trained = False
        self.top_k = -1
    
    def set_int_to_label(self, int_to_label):
        self.int_to_label = int_to_label
    def train(self, acoustic_training_dataset, wifi_training_dataset, acoustic_test_dataset, wifi_test_dataset):
        with self.training_lock:
            acoustic_train_set, acoustic_train_label = acoustic_training_dataset
            acoustic_test_set, acoustic_test_label = acoustic_test_dataset
            wifi_train_set, wifi_train_label = wifi_training_dataset
            wifi_test_set, wifi_test_label = wifi_test_dataset
            
            best_k = 2
            best_accuracy = "NAN"
            # best_k = -1
            # best_accuracy = -1
            # for k in range(1, len(self.int_to_label) + 1):
            #     accuracy = self.two_step_test_accuracy(acoustic_train_set, wifi_train_set, wifi_train_label, k, False)
            #     if best_accuracy < accuracy:
            #         best_k = k
            #         best_accuracy = accuracy
            
            test_accuracy = self.two_step_test_accuracy(acoustic_test_set, wifi_test_set, wifi_test_label, best_k, True)
            print("BEST K:" + str(best_k) + " TRAIN_ACCURACY:" + str(best_accuracy) + " TEST_ACCURACY:" + str(test_accuracy))
            self.top_k = best_k
            self.model_trained = True
            return test_accuracy

    def get_prediction(self, acoustic_sample, wifi_sample, top_k=None):
        if top_k == None:
            top_k = self.top_k
        
        wifi_top = wifi_top_k(self.wifi_model, top_k, wifi_sample)
        acoustic_top = acoustic_top_k(self.acoustic_model, 1000, acoustic_sample)
        for top_choice in acoustic_top:
            if np.any(wifi_top == top_choice):
                return top_choice

    def classify(self, acoustic_sample, wifi_sample):
        return self.int_to_label[self.get_prediction(acoustic_sample, wifi_sample)]

    def two_step_test_accuracy(self, acoustic_test, wifi_test, labels, top_k, save_matrix):

        combined_predictions = []
        for acoustic_sample, wifi_sample in zip(acoustic_test, wifi_test):
            combined_predictions.append(self.get_prediction(acoustic_sample, wifi_sample, top_k))
        combined_predictions = np.asarray(combined_predictions)

        accuracy = accuracy_score(labels, combined_predictions)
        if save_matrix:
            create_confusion_matrix(labels, combined_predictions, self.int_to_label, accuracy, "two_step_top_k_" + str(self.top_k))



        return accuracy


def wifi_top_k(wifi_model, top_k, wifi_sample):
    wifi_prediction = wifi_model.classify_probability(np.reshape(wifi_sample, (1,len(wifi_sample))))[0]
    wifi_top = wifi_prediction.argsort()[-top_k:][::-1]
    return wifi_top

def acoustic_top_k(acoustic_model, top_k, acoustic_sample):
    acoustic_prediction = acoustic_model.get_predictions(acoustic_sample)[0]
    acoustic_top = acoustic_prediction.argsort()[-top_k:][::-1]
    return acoustic_top

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

    create_confusion_matrix(labels, combined_predictions, int_to_label, accuracy, "top_k_wifi")
    
    return accuracy


def acoustic_top_k_test_accuracy(acoustic_model, top_k, acoustic_test, labels):
    int_to_label = acoustic_model.get_int_to_label()
    acoustic_top = []
    for acoustic_sample in acoustic_test:
        acoustic_top.append(acoustic_top_k(acoustic_model, top_k, acoustic_sample))
    combined_predictions = []
    for i, top_list in enumerate(acoustic_top):
        if np.any(top_list == labels[i]):
            combined_predictions.append(labels[i])
        else:
            combined_predictions.append(top_list[0])
    accuracy = accuracy_score(labels, combined_predictions)

    create_confusion_matrix(labels, combined_predictions, int_to_label, accuracy, "top_k_acoustic")
    
    return accuracy



def wifi_top_k_to_string(wifi_model, top_k, wifi_sample):
    int_to_label = wifi_model.get_int_to_label()
    wifi_prediction = wifi_model.classify_probability(np.reshape(wifi_sample, (1,len(wifi_sample))))[0]
    wifi_top = wifi_prediction.argsort()[-top_k:][::-1]
    accuracy = np.sort(wifi_prediction)[::-1]
    string_list = []
    for wifi_label, acc in zip(wifi_top, accuracy):
        string_list.append(int_to_label[wifi_label] + " " + str(round(acc, 2)))

    return string_list


def acoustic_top_k_to_string(acoustic_model, top_k, acoustic_sample):
    int_to_label = acoustic_model.get_int_to_label()
    acoustic_prediction = acoustic_model.get_predictions(acoustic_sample)[0]
    acoustic_top = acoustic_prediction.argsort()[-top_k:][::-1]
    accuracy = np.sort(acoustic_prediction)[::-1]
    string_list = []

    for acoustic_label, acc in zip(acoustic_top, accuracy):
        string_list.append(int_to_label[acoustic_label] + " " + str(round(acc, 2)))

    return string_list
