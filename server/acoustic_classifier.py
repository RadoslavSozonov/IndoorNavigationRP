import tensorflow as tf

from tensorflow.keras import datasets, layers, models
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from PIL import Image

import numpy as np
import os

class AcousticClassifier:
    def __init__(self):
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
        self.model.add(layers.Dense(2))


    def train(self):

        self.model.summary()
        
        images = []
        labels = []
        int_to_label = []
        count = 0
        for building_label in next(os.walk('./images'))[1]:
            for room_label in next(os.walk('./images/' + building_label))[1]:
                
                full_path = './images/' + building_label + '/' + room_label
                files = (file for file in os.listdir(full_path) 
                        if os.path.isfile(os.path.join(full_path, file)))
                for sample in files:
                    grey = Image.open(full_path + '/' +sample)
                    grey = np.asarray(grey)
                    full_label = building_label + '_' + room_label
                    images.append(grey)
                    labels.append(count)
                    int_to_label.append((count, full_label))

                count = count + 1
        images = np.asarray(images)
        labels = np.asarray(labels)

        images_train, images_test, labels_train, labels_test = train_test_split(images, labels, test_size=0.5, random_state=42)

        self.model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

        history = self.model.fit(images_train, labels_train, epochs=200, 
                    validation_data=(images_test, labels_test))

        
        plt.plot(history.history['accuracy'], label='accuracy')
        plt.plot(history.history['val_accuracy'], label = 'val_accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.ylim([0.5, 1])
        plt.legend(loc='lower right')

        plt.show()


acoustic_classifier = AcousticClassifier()

acoustic_classifier.train()


