import pickle
import time
from os import listdir
import tensorflow as tf
from DeepModels.DTCSingelton import DTCSingelton
from sklearn.tree import DecisionTreeClassifier


class DTCModel(DTCSingelton):
    def __init__(self):
        self.dct_models = {}

    def create_new_model(
            self,
            name_of_model,
            model_info
    ):
        criterion = "gini"
        splitter = "best"
        max_features = "auto"

        if "criterion" in model_info:
            criterion = model_info["criterion"]
        if "splitter" in model_info:
            splitter = model_info["splitter"]
        if "max_features" in model_info:
            max_features = model_info["max_features"]
        name_of_model += "_"+str(criterion)
        model = DecisionTreeClassifier(criterion=criterion, splitter=splitter, max_features=max_features)
        self.dct_models[name_of_model] = model
        return name_of_model

    def train(self, name_of_model, training_set, training_labels):
        start_time = time.time()
        self.dct_models[name_of_model] = self.dct_models[name_of_model].fit(
            training_set,
            training_labels
        )
        pickle.dump(self.dct_models[name_of_model], open("models/dct_models/" + name_of_model + ".pickle", "wb"))
        return self.dct_models[name_of_model], int(time.time()-start_time)

    def predict(self, name_of_model, input_image):
        return self.dct_models[name_of_model].predict(input_image)

    def evaluate(self, name_of_model, test_set, test_labels):
        test_acc = self.dct_models[name_of_model] \
            .score(
            test_set,
            test_labels
        )
        return test_acc

    # @staticmethod
    # def load_models(self, path):
    #     for model_name in listdir(path):
    #         model = self.models.load_model(path + model_name)
    #         self.dtc_models[model.split(".")[0]] = model