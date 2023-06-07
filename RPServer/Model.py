import tensorflow as tf
import numpy as np

class Model:
    def __init__(self):
        self.x = "data"

    def train(self, training_data, labels):

        num_classes = 2
        sample_length = len(training_data[0])

        # model = tf.keras.Sequential([
        #     tf.keras.layers.Conv1D(32, 3, activation='relu', input_shape=(sample_length, 1)),
        #     tf.keras.layers.MaxPooling1D(2),
        #     tf.keras.layers.Conv1D(64, 3, activation='relu'),
        #     tf.keras.layers.MaxPooling1D(2),
        #     tf.keras.layers.Flatten(),
        #     tf.keras.layers.Dense(128, activation='relu'),
        #     tf.keras.layers.Dense(num_classes, activation='softmax')
        # ])

        model = tf.keras.Sequential([
            tf.keras.layers.Conv1D(16, 3, activation='relu', input_shape=(sample_length, 1)),
            tf.keras.layers.GlobalMaxPooling1D(),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(num_classes, activation='softmax')
        ])

        training_data = training_data / np.max(np.abs(training_data))


        training_data = tf.convert_to_tensor(training_data, dtype=tf.float32)
        labels = tf.convert_to_tensor(labels, dtype=tf.float32)

        train_ratio = 0.7
        val_ratio = 0.15
        test_ratio = 0.15

        num_samples = len(training_data)
        num_train = int(train_ratio * num_samples)
        num_val = int(val_ratio * num_samples)

        train_audio = training_data[:num_train]
        train_labels = labels[:num_train]
        val_audio = training_data[num_train:num_train + num_val]
        val_labels = labels[num_train:num_train + num_val]
        test_audio = training_data[num_train + num_val:]
        test_labels = labels[num_train + num_val:]

        loss_function = tf.keras.losses.CategoricalCrossentropy()
        optimizer = tf.keras.optimizers.Adam() 

        batch_size = 2
        epochs = 10

        train_labels = tf.keras.utils.to_categorical(train_labels, num_classes)
        val_labels = tf.keras.utils.to_categorical(val_labels, num_classes)
        test_labels = tf.keras.utils.to_categorical(test_labels, num_classes)

        print(train_labels)

        model.compile(loss=loss_function, optimizer=optimizer, metrics=['accuracy'])
        model.fit(train_audio, train_labels, batch_size=batch_size, epochs=epochs, validation_data=(val_audio, val_labels))

        # Step 8: Evaluate the model

        test_loss, test_accuracy = model.evaluate(test_audio, test_labels)
        print('Test Loss:', test_loss)
        print('Test Accuracy:', test_accuracy)

        self.model = model

        return

    def predict(self, audio_sample):
        return self.model.predict(audio_sample)