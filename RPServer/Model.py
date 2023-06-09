import tensorflow as tf
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten

class Model:
    def __init__(self):
        self.x = "data"

    def train(self, sound_data, labels):

        # Convert labels to numerical values
        label_to_id = {label: i for i, label in enumerate(set(labels))}
        id_to_label = {i: label for label, i in label_to_id.items()}
        numerical_labels = np.array([label_to_id[label] for label in labels])

        # Normalize sound data
        sound_data = (sound_data - np.mean(sound_data)) / np.std(sound_data)

        # Split the dataset into training and testing sets
        split_ratio = 0.8  # 80% training, 20% testing
        split_index = int(len(sound_data) * split_ratio)

        train_data, test_data = sound_data[:split_index], sound_data[split_index:]
        train_labels, test_labels = numerical_labels[:split_index], numerical_labels[split_index:]

        model = Sequential()
        model.add(Flatten(input_shape=(sound_data.shape[1],)))  # Flatten the input
        model.add(Dense(128, activation='relu'))
        model.add(Dense(len(label_to_id), activation='softmax'))  # Output layer with softmax activation

        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        model.fit(train_data, train_labels, epochs=10, batch_size=2)

        test_loss, test_accuracy = model.evaluate(test_data, test_labels)
        print(f'Test Loss: {test_loss:.4f}')
        print(f'Test Accuracy: {test_accuracy:.4f}')

        self.model = model
        self.id_to_label = id_to_label

        return

    def predict(self, audio_sample):
        return self.model.predict(audio_sample)