from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from sklearn import svm
from threading import Lock
from utils import create_confusion_matrix


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
        self.int_to_label = int_to_label
        with self.training_lock:
            if self.mode == "KNN":
                self.model = KNeighborsClassifier(n_neighbors=1, probability=True)
                self.model.fit(wifi_train, labels_train)
            elif self.mode == "SVM":
                self.model = svm.SVC(kernel='linear', probability=True)
                self.model.fit(wifi_train, labels_train)
            else:
                print("INVALID WIFI MODE NAME")
                return
        
            self.model_trained = True

    def classify(self, sample):
        sample = np.asarray(sample)
        with self.training_lock:
            if self.model_trained:
                return self.int_to_label[self.model.predict(np.reshape(sample,(1, len(sample))))[0]]
            else:
                return "Model is not trained yet"

    def test_accuracy(self, tests, labels):
        with self.training_lock:
            if self.model_trained:
                wifi_predictions = self.model.predict(tests)
                accuracy = accuracy_score(labels, wifi_predictions)
                create_confusion_matrix(labels, wifi_predictions, np.asarray(self.int_to_label),accuracy, "wifi")
                return accuracy
            else:
                return "Model is not trained yet"

    def classify_probability(self, sample):
        with self.training_lock:
            if self.model_trained:
                return self.model.predict_proba(sample)
            else:
                return "Model is not trained yet"

    def get_int_to_label(self):
        return np.asarray(self.int_to_label)




if __name__ == "__main__":
    
    wifis, wifi_labels, wifi_int_to_label = db.get_wifi_training_set()
    room_amount = db.get_room_amount()
    wifi_dataset = train_test_split(wifis, wifi_labels, test_size=test_split, random_state=42)
    acoustic_model.train(acoustic_dataset, image_int_to_label, room_amount)
    wifi_model.train(wifi_dataset, wifi_int_to_label, room_amount)

    test_classifiers(acoustic_dataset[1], acoustic_dataset[3], wifi_dataset[1], wifi_dataset[3])