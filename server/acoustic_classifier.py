import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

from tensorflow.keras import datasets, layers, models
from threading import Lock
from utils import create_confusion_matrix
from sklearn.metrics import accuracy_score
from threading import Lock

class AcousticClassifier:
    def __init__(self):
        self.int_to_label = []
        self.model = None
        self.training_lock = Lock()
        self.model_trained = False

    def train(self, dataset, int_to_label, room_amount, filename=None):
        # setup the model
        with self.training_lock:
            self.int_to_label = int_to_label
            if filename == None:
                self.model = models.Sequential()
                self.model.add(
                            layers.Conv2D(
                                16,
                                (4, 4),
                                activation='relu',
                                input_shape=(5,32, 1),
                                strides=(1, 1),
                                padding="same"
                            )
                        )
                self.model.add(layers.MaxPooling2D(
                            (
                                2,
                                2,
                            ),
                            strides=(2, 2),
                            padding="valid"
                        ))

                self.model.add(
                            layers.Conv2D(
                                32,
                                (4, 4),
                                activation='relu',
                                input_shape=(5,32, 1),
                                strides=(1, 1),
                                padding="same"
                            )
                        )
                self.model.add(layers.MaxPooling2D(
                            (
                                2,
                                2,
                            ),
                            strides=(2, 2),
                            padding="valid"
                        ))

                self.model.add(layers.Flatten())
                
                self.model.add(layers.Dense(1024, activation='relu'))
                self.model.add(layers.Dropout(0.4))
                self.model.add(layers.Dense(room_amount, activation='softmax'))

                self.model.compile(optimizer='adam',
                    loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
                    metrics=['accuracy'])

                self.model.summary()
                print("room amount: " + str(room_amount))

                # Split the data into training and test set


                train_set, train_labels, validation_set, validation_labels, _, _ = dataset

                # print("training set size: " + str(np.size(images_train)))
                # print("test set size: " + str(np.size(images_test)))

                # train the model
                history = self.model.fit(train_set, tf.keras.utils.to_categorical(train_labels, room_amount), epochs=100, 
                            validation_data=(validation_set, tf.keras.utils.to_categorical(validation_labels, room_amount)))

                # plt.plot(history.history['accuracy'], label='accuracy')
                # plt.plot(history.history['val_accuracy'], label = 'val_accuracy')
                # plt.xlabel('Epoch')
                # plt.ylabel('Accuracy')
                # plt.ylim([0.5, 1])
                # plt.legend(loc='lower right')

                # plt.savefig("./metadata/current_model_accuracy.png")

                # # Clear the plot
                # plt.clf()
                self.save_model("best_acoustic.h5")

            else:
                self.load_model(filename)

            self.model_trained = True



    def save_model(self, filename):
        self.model.save('./models/' + filename)

    def test_accuracy(self, test_images, test_labels):
        # test_loss, test_acc = self.model.evaluate(test_images,  tf.keras.utils.to_categorical(test_labels, 14), verbose=2)
        acoustic_predictions = []
        for i, acoustic_sample in enumerate(test_images):
            x = self.get_predictions(acoustic_sample)
            acoustic_predictions.append(np.argmax(x))
        accuracy = accuracy_score(test_labels, acoustic_predictions)
        create_confusion_matrix(test_labels, acoustic_predictions, np.asarray(self.int_to_label),accuracy, "acoustic")
        return accuracy
    def load_model(self, filename):
        self.model = models.load_model('./models/' + filename)

    def get_predictions(self, sample):
        with self.training_lock:
            if self.model_trained:
                return self.model.predict(np.array([sample,]))
            else:
                return "Model is not trained yet"
    def get_int_to_label(self):
        return np.asarray(self.int_to_label)
    def classify(self, sample):
        with self.training_lock:
            if self.model_trained:
                
                weights = self.model.predict(np.array([sample,]))
                return self.int_to_label[np.argmax(weights)]
            else:
                return "Model is not trained yet"


if __name__ == "__main__":
    acoustic_classifier = AcousticClassifier()
    acoustic_classifier.train()