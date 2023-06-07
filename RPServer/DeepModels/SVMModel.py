from os import listdir
import tensorflow as tf
from sklearn.svm import LinearSVC
from DeepModels.SVMSingelton import SVMSingelton
import time
import pickle


class SVMModel(SVMSingelton):

    linearSVC_models = {}

    def __init__(self):
        pass

    def create_new_model(
            self,
            name_of_model,
            model_info
    ):
        penalty = "l2",
        loss = "squared_hinge",
        tol = 0.0001,
        C = 1,
        max_iter = 1000,
        dual = False
        if "penalty" in model_info:
            penalty = model_info["penalty"]
        if "loss" in model_info:
            loss = model_info["loss"]
        if "tol" in model_info:
            tol = model_info["tol"]
        if "C" in model_info:
            C = model_info["C"]
        if "max_iter" in model_info:
            max_iter = model_info["max_iter"]

        name_of_model += "_" + str(penalty) + "_" +str(C)
        model = LinearSVC(penalty=penalty, loss=loss, tol=tol, C=C, dual=dual, max_iter=max_iter)
        self.linearSVC_models[name_of_model] = model
        return name_of_model

    def train(self, name_of_model, training_set, training_labels):
        start_time = time.time()
        self.linearSVC_models[name_of_model] = self.linearSVC_models[name_of_model].fit(
            training_set,
            training_labels
        )
        pickle.dump(self.linearSVC_models[name_of_model], open("models/linearSVC_models/" + name_of_model + ".pickle", "wb"))
        return self.linearSVC_models[name_of_model], int(time.time()-start_time)

    def predict(self, name_of_model, input_image):
        return self.linearSVC_models[name_of_model].predict(input_image)

    def evaluate(self, name_of_model, test_set, test_labels):
        test_acc = self.linearSVC_models[name_of_model] \
            .score(
            test_set,
            test_labels
        )
        return test_acc

    @staticmethod
    def load_models(self, path):
        for model_name in listdir(path):
            model = self.models.load_model(path + model_name)
            self.linearSVC_models[model.split(".")[0]] = model