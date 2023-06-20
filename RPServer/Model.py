import tensorflow as tf
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras import datasets, layers, models
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import json
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import globals

import random

class Model:
    def __init__(self):
        self.save_folder = "database\\"

    def load(self):
        self.model = models.load_model(self.save_folder + "CNNmodel.h5")
        with open(self.save_folder + "labels.json", "r") as file:
            self.labels = json.load(file)

    def save(self, type):
        with open(self.save_folder + type + "\\labels.json", "w") as file:
            file.write(json.dumps(self.labels))
        self.model.save(self.save_folder + type + '\\CNNmodel.h5')

    def train(self, sound_data, labels, label_amount, type):

        # Convert labels to numerical values
        # id_to_label = [label for label in labels]
        # numerical_labels = np.array([label_to_id[label] for label in labels])

        # label_to_id = {label: i for i, label in enumerate(set(labels))}
        # id_to_label = {i: label for label, i in label_to_id.items()}
        # numerical_labels = np.array([label_to_id[label] for label in labels])

        named_labels = []
        label_to_id = {}

        for i, label in enumerate(set(labels)):
            named_labels.append(label)
            label_to_id[label] = i

        numerical_labels = np.array([label_to_id[label] for label in labels])
       

        # Normalize sound data
        sound_data = (sound_data - np.mean(sound_data)) / np.std(sound_data)

        # Split the dataset into training and testing sets
        split_ratio = 0.8  # 80% training, 20% testing

        train_data, train_labels, validation_set, validation_labels, test_set, test_labels = self.split_data(sound_data, numerical_labels, split_ratio)

        print(label_amount)

        print(np.shape(train_data))
        print(np.shape(train_labels))
        print(np.shape(validation_set))
        print(np.shape(validation_labels))

        model = models.Sequential()
        model.add(
            layers.Conv2D(
                16,
                (4,4),
                activation='relu',
                input_shape=(5,32,1),
                strides=(1,1),
                padding="same"
            )
        )

        model.add(layers.MaxPooling2D (
            (2,2,),
            strides=(2,2),
            padding="valid"
        ))

        model.add(
            layers.Conv2D(
            32,
            (4,4),
            activation='relu',
            input_shape=(5,32,1),
            strides=(1,1),
            padding="same"
            )
        )
        model.add(layers.MaxPooling2D(
            (2,2,),
            strides=(2,2),
            padding="valid"
        ))

        model.add(layers.Flatten())
        model.add(layers.Dense(1024, activation='relu'))
        model.add(layers.Dropout(0.4))
        model.add(layers.Dense(label_amount, activation='softmax'))

        model.compile(optimizer='adam', loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True), metrics=['accuracy'])
        model.summary()

        history = model.fit(train_data, tf.keras.utils.to_categorical(train_labels, label_amount), epochs=100, 
                            validation_data=(validation_set, tf.keras.utils.to_categorical(validation_labels, label_amount)))
        
        

        plt.clf()
        plt.plot(history.history['accuracy'], label='accuracy')
        plt.plot(history.history['val_accuracy'], label = 'val_accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.ylim([0.0, 1])
        plt.legend(loc='lower right')

        plt.savefig(self.save_folder  + type + "\\performance.png")
        plt.clf()

        self.model = model
        self.labels = named_labels

        self.create_confusion_matrix(test_set, test_labels, type)

        self.save(type)
        return

    def predict(self, audio_sample):
        return self.model.predict(audio_sample)
    
    def create_confusion_matrix(self, test_data, test_labels, type):
        predicted_labels = []

        print(np.shape(test_data))

        for i in range(len(test_data)):
            print(np.shape(np.expand_dims(test_data[i], axis=0)))
            predicted_labels.append(np.argmax(self.model.predict(np.expand_dims(test_data[i], axis=0))))

        matrix = confusion_matrix(predicted_labels, test_labels)

        print(np.shape(matrix))

        plt.clf()
        _, ax = plt.subplots(figsize=(12, 12))
        display = ConfusionMatrixDisplay(confusion_matrix=matrix, display_labels=self.labels)
        display.plot(ax=ax, xticks_rotation="vertical", cmap=plt.cm.Blues)
        plt.savefig(self.save_folder + type + "\\confusion_matrix.png", bbox_inches="tight")
        plt.clf()

        return
    
    def split_data(self, data, labels, _):

        training_set, temp, training_labels , temp_l = train_test_split(data, labels, test_size=0.2, random_state=42)

        validation_set, test_set, validation_labels, test_labels = train_test_split(temp, temp_l, test_size=0.5, random_state=42)

        return training_set, training_labels, validation_set, validation_labels, test_set, test_labels