from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import GridSearchCV
from sklearn import svm
from threading import Lock
from utils import create_confusion_matrix
import numpy as np
import pickle

knn_param_grid = {
    'n_neighbors': [1,2,3,4,5,6,7,8,9,10],  
    'weights': ['uniform', 'distance']
}

svm_param_grid = {
    'C': [0.1, 1, 10],
    'kernel': ['linear', 'rbf', 'poly', 'sigmoid'],
    'gamma': ['scale', 'auto', 0.1, 1],
    'degree': [2, 3, 4],
    'class_weight': [None, 'balanced'],
    'decision_function_shape': ['ovo', 'ovr']
}


class WifiClassifier:
    def __init__(self):
        self.int_to_label = []
        self.model = None
        self.training_lock = Lock()
        self.model_trained = False
    def train(self, dataset, int_to_label, room_amount, filename=None):
        train_set, train_labels, validation_set, validation_labels= dataset
        self.int_to_label = int_to_label
        with self.training_lock:
            if filename == None:
                knn_model = KNeighborsClassifier()
                knn_grid_search = GridSearchCV(knn_model, knn_param_grid)
                knn_grid_search.fit(train_set, train_labels)

                svm_model = svm.SVC(probability=True)
                svm_grid_search = GridSearchCV(svm_model, svm_param_grid)
                svm_grid_search.fit(train_set, train_labels)
                
                best_knn_params = knn_grid_search.best_params_
                best_svm_params = svm_grid_search.best_params_
                best_knn_score = knn_grid_search.best_score_
                best_svm_score = svm_grid_search.best_score_
                print("KNN PARAMS: " + str(best_knn_params) + "\nACCURACY: " + str(best_knn_score))
                print("SVM PARAMS: " + str(best_svm_params) + "\nACCURACY: " + str(best_svm_score))

                if best_knn_score > best_svm_score:
                    print("KNN CHOSEN")
                    self.model = knn_grid_search.best_estimator_
                else:
                    print("SVM CHOSEN")
                    self.model = svm_grid_search.best_estimator_

                # knn_results = knn_grid_search.cv_results_
                # svm_results = svm_grid_search.cv_results_
                # knn_combinations = zip(knn_results['params'], knn_results['mean_test_score'])
                # svm_combinations = zip(svm_results['params'], svm_results['mean_test_score'])
                # for params, accuracy in knn_combinations:
                #     print("Parameters:", params, "Accuracy:", accuracy)
                # for params, accuracy in svm_combinations:
                #     print("Parameters:", params, "Accuracy:", accuracy)

                pickle.dump(self.model, open("./models/best_wifi.sav", 'wb'))
            else:
                self.model = pickle.load(open(filename, 'rb'))
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