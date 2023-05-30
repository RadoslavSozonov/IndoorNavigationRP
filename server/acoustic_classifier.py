import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

from tensorflow.keras import datasets, layers, models
from sklearn.model_selection import train_test_split
from database import LocalDatabase
from threading import Lock

class AcousticClassifier:
    def __init__(self):
        self.db = LocalDatabase()
        self.int_to_label = []
        self.model = None
        self.training_lock = Lock()
        self.model_trained = False

    def train(self, test_split=0.8):
        # setup the model
        with self.training_lock:
            room_amount = self.db.get_room_amount()
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
            
            self.model.add(layers.Dense(1024))
            self.model.add(layers.Dropout(0.4))
            self.model.add(layers.Dense(room_amount))

            self.model.compile(optimizer='adam',
                loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                metrics=['accuracy'])

            self.model.summary()
            print("room amount: " + str(room_amount))

            
            # Split the data into training and test set
            images, labels, int_to_label = self.db.get_training_set()
            self.int_to_label = int_to_label
            images_train, images_test, labels_train, labels_test = train_test_split(images, labels, test_size=test_split, random_state=42)

            print("training set size: " + str(np.size(images_train)))
            print("test set size: " + str(np.size(images_test)))

            # train the model
            history = self.model.fit(images_train, labels_train, epochs=200, 
                        validation_data=(images_test, labels_test))

            
            plt.plot(history.history['accuracy'], label='accuracy')
            plt.plot(history.history['val_accuracy'], label = 'val_accuracy')
            plt.xlabel('Epoch')
            plt.ylabel('Accuracy')
            plt.ylim([0.5, 1])
            plt.legend(loc='lower right')

            plt.savefig("current_model_accuracy.png")

            # Clear the plot
            plt.clf()

            self.model_trained = True


    def save_model(self, filename):
        with self.training_lock:
            self.model.save('./models/' + filename)

    def load_model(self, filename):
        with self.training_lock:
            self.model = models.load_model('./models/' + filename)

    def classify(self, sample):
        with self.training_lock:
            if self.model_trained:
                weights = self.model.predict(np.array([sample,]))
                print(weights)
                print(self.int_to_label)
                return self.int_to_label[np.argmax(weights)]
            else:
                return "Model is not trained yet"

# acoustic_classifier = AcousticClassifier()
# acoustic_classifier.train()


