import pickle
import time
from os import listdir
import tensorflow as tf
from sklearn.neighbors import KNeighborsClassifier
from DeepModels.KNNSingelton import KNNSingelton


class KNNModel(KNNSingelton):
    knn_models = {}

    def __init__(self):
        pass

    def create_new_model(
            self,
            name_of_model,
            model_info

    ):
        n_neighbors = 5,
        weights = "uniform",
        algorithm = "auto",
        n_jobs = 1

        if "n_neighbors" in model_info:
            n_neighbors = model_info["n_neighbors"]
        if "weights" in model_info:
            weights = model_info["weights"]
        if "algorithm" in model_info:
            algorithm = model_info["algorithm"]
        if "n_jobs" in model_info:
            n_jobs = model_info["n_jobs"]
        name_of_model += "_" + str(n_neighbors) + "_" + str(weights)
        model = KNeighborsClassifier(n_neighbors=n_neighbors, weights=weights, algorithm=algorithm, n_jobs=n_jobs)
        self.knn_models[name_of_model] = model
        return name_of_model

    def train(self, name_of_model, training_set, training_labels):
        start_time = time.time()
        self.knn_models[name_of_model] = self.knn_models[name_of_model].fit(
            training_set,
            training_labels
        )
        pickle.dump(self.knn_models[name_of_model], open("models/knn_models/" + name_of_model + ".pickle", "wb"))

        # self.knn_models[name_of_model].save("models/knn_models/" + name_of_model + ".h5")
        return self.knn_models[name_of_model], int(time.time()-start_time)

    def predict(self, name_of_model, input_image):
        return self.knn_models[name_of_model].predict(input_image)

    def evaluate(self, name_of_model, test_set, test_labels):
        test_acc = self.knn_models[name_of_model] \
            .score(
            test_set,
            test_labels
        )
        return test_acc

    def load_models(self, path):
        for model_name in listdir(path):
            model = pickle.load(open(path + model_name, 'rb'))
            # print("knn_" + model_name.split(".")[0])
            self.knn_models["knn_"+model_name.split(".")[0].replace("-", "_")] = model
        # print(self.knn_models)