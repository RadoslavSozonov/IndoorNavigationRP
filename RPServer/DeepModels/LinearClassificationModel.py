import pickle
import time
from os import listdir
import tensorflow as tf
from sklearn.linear_model import SGDClassifier
from DeepModels.LinearClassificationSingelton import LinearClassificationSingelton


class LinearClassificationModel(LinearClassificationSingelton):
    sgd_models = {}

    def __init__(self):
        pass

    def create_new_model(
            self,
            name_of_model,
            model_info

    ):
        loss = "hinge",
        penalty = "l2",
        alpha = 0.00001,
        l1_ratio = 0.15,
        max_iter = 1000,
        tol = 0.0001

        if "penalty" in model_info:
            penalty = model_info["penalty"]
        if "loss" in model_info:
            loss = model_info["loss"]
        if "tol" in model_info:
            tol = model_info["tol"]
        if "l1_ratio" in model_info:
            l1_ratio = model_info["l1_ratio"]
        if "max_iter" in model_info:
            max_iter = model_info["max_iter"]
        if "alpha" in model_info:
            alpha = model_info["alpha"]

        name_of_model += "_" + str(l1_ratio) + "_" + str(alpha)

        model = SGDClassifier(loss=loss, penalty=penalty, alpha=alpha, l1_ratio=l1_ratio, tol=tol, max_iter=max_iter)
        self.sgd_models[name_of_model] = model
        return name_of_model

    def train(self, name_of_model, training_set, training_labels):
        start_time = time.time()
        self.sgd_models[name_of_model] = self.sgd_models[name_of_model].fit(
            training_set,
            training_labels
        )
        pickle.dump(self.sgd_models[name_of_model], open("models/sgd_models/" + name_of_model + ".pickle", "wb"))
        # self.sgd_models[name_of_model].save("models/sgd_models/" + name_of_model + ".h5")
        return self.sgd_models[name_of_model], int(time.time()-start_time)

    def predict(self, name_of_model, input_image):
        return self.sgd_models[name_of_model].predict(input_image)

    def evaluate(self, name_of_model, test_set, test_labels):
        test_acc = self.sgd_models[name_of_model] \
            .score(
            test_set,
            test_labels
        )
        return test_acc

    def load_models(self, path):
        for model_name in listdir(path):
            model = pickle.load(open(path + model_name, 'rb'))
            # print("sgd_" + model_name.split(".")[0])
            self.sgd_models["sgd_"+model_name.split(".")[0].replace("-", "_")] = model
        # print(self.sgd_models)