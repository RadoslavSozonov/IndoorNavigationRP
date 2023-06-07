from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from sklearn import svm
from threading import Lock


import numpy as np

class WifiClassifier:
    def __init__(self, mode):
        self.int_to_label = []
        self.mode = mode
        self.model = None
        self.training_lock = Lock()
        self.model_trained = False
    def train(self, dataset, int_to_label, room_amount):
        wifi_train, wifi_test, labels_train, labels_test = dataset
        with self.training_lock:
            if self.mode == "KNN":
                self.model = KNeighborsClassifier(n_neighbors=1)
                self.model.fit(wifi_train, labels_train)
            elif self.mode == "SVM":
                self.model = svm.SVC(kernel='linear')
                self.model.fit(wifi_train, labels_train)
            else:
                print("INVALID WIFI MODE NAME")
                return
        
            self.model_trained = True

    def classify(self, sample):
        with self.training_lock:
            if self.model_trained:
                return self.model.predict(sample)
            else:
                return "Model is not trained yet"
