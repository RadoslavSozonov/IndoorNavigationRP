import tensorflow as tf
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras import datasets, layers, models
import matplotlib.pyplot as plt

import random

class Model:
    def __init__(self):
        self.x = "data"

    def train(self, sound_data, labels, label_amount):

        # Convert labels to numerical values
        label_to_id = {label: i for i, label in enumerate(set(labels))}
        id_to_label = {i: label for label, i in label_to_id.items()}
        numerical_labels = np.array([label_to_id[label] for label in labels])

        # Normalize sound data
        sound_data = (sound_data - np.mean(sound_data)) / np.std(sound_data)

        # Split the dataset into training and testing sets
        split_ratio = 0.8  # 80% training, 20% testing

        train_data, train_labels, validation_set, validation_labels = self.split_data(sound_data, numerical_labels, split_ratio)

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
        
        model.save('CNNmodel.h5')

        plt.plot(history.history['accuracy'], label='accuracy')
        plt.plot(history.history['val_accuracy'], label = 'val_accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.ylim([0.5, 1])
        plt.legend(loc='lower right')

        plt.savefig("./metadata/current_model_accuracy.png")
        plt.clf()

        self.model = model
        self.id_to_label = id_to_label

        return

    def predict(self, audio_sample):
        return self.model.predict(audio_sample)
    
    def split_data(self, data, labels, split_ratio):
        
        split_value = int(len(data) * (1 - split_ratio))

        print(split_value)

        validation_data = []
        validation_labels = []

        del_indices = []

        for i in range(split_value):
            del_index = random.randrange(len(data))

            validation_data.append(data[del_index])
            validation_labels.append(labels[del_index])

            del_indices.append(del_index)

        del_indices = sorted(del_indices, reverse=True)

        for i in del_indices:
            data = np.delete(data, i, 0)
            labels = np.delete(labels, i)
        

        return data, labels, validation_data, validation_labels