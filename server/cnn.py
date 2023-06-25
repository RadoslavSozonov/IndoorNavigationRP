import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import tensorflow as tf
import sklearn

from keras import layers, losses
from keras.models import Model, Sequential
from sklearn.metrics import ConfusionMatrixDisplay


class CNN(Model):
  def __init__(self):
    super(CNN, self).__init__()

  def trainPassive(self, x_train, x_test, y_train, y_test):


    self.model = Sequential()

    self.model.add(layers.Conv2D(16, (4, 4), activation='relu', input_shape=(5, 342, 1), padding="same", strides=(1,1)))
    self.model.add(layers.MaxPooling2D((2, 2), strides=(2,2), padding='valid'))
    self.model.add(layers.Conv2D(32, (4, 4), activation='relu', input_shape=(5, 342, 1), padding="same", strides=(1,1)))
    self.model.add(layers.MaxPooling2D((2, 2), strides=(2,2), padding='valid'))
    self.model.add(layers.Flatten())
    self.model.add(layers.Dense(1024, activation='relu'))
    self.model.add(layers.Dropout(0.4))
    self.model.add(layers.Dense(6, activation='softmax'))


    self.model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(),
              metrics=['accuracy'])

    history = self.model.fit(x_train, y_train, epochs=100, 
                    validation_data=(x_test, y_test))
    
    # plt.plot(history.history['accuracy'], label='accuracy')
    # plt.plot(history.history['val_accuracy'], label = 'val_accuracy')
    # plt.xlabel('Epoch')
    # plt.ylabel('Accuracy')
    # plt.ylim([0.5, 1])
    # plt.legend(loc='lower right')
    # test_loss, test_acc = self.model.evaluate(x_test,  y_test, verbose=2)
    # plt.savefig("modeltest" + ".png")
    # plt.clf

    return "abc "
  
  def trainActive(self, x_train, x_test, y_train, y_test):


    self.model = Sequential()

    self.model.add(layers.Conv2D(16, (4, 4), activation='relu', input_shape=(5, 32, 1), padding="same", strides=(1,1)))
    self.model.add(layers.MaxPooling2D((2, 2), strides=(2,2), padding='valid'))
    self.model.add(layers.Conv2D(32, (4, 4), activation='relu', input_shape=(5, 32, 1), padding="same", strides=(1,1)))
    self.model.add(layers.MaxPooling2D((2, 2), strides=(2,2), padding='valid'))
    self.model.add(layers.Flatten())
    self.model.add(layers.Dense(1024, activation='relu'))
    self.model.add(layers.Dropout(0.4))
    self.model.add(layers.Dense(6, activation='softmax'))


    self.model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(),
              metrics=['accuracy'])

    history = self.model.fit(x_train, y_train, epochs=100, 
                    validation_data=(x_test, y_test))
    
    # plt.plot(history.history['accuracy'], label='accuracy')
    # plt.plot(history.history['val_accuracy'], label = 'val_accuracy')
    # plt.xlabel('Epoch')
    # plt.ylabel('Accuracy')
    # plt.ylim([0.5, 1])
    # plt.legend(loc='lower right')
    # test_loss, test_acc = self.model.evaluate(x_test,  y_test, verbose=2)
    # plt.savefig("modeltest" + ".png")
    # plt.clf

    return "abc "
  
  
  
  def save(self, mode):
    self.model.save(mode + '_model.h5')
  
  def load(self, mode):
    self.model = tf.keras.models.load_model(mode + '_model.h5')

  def plot_confusion_matrix(self, actual, predicted, labels, ds_type):

    #sklearn.metrics.confusion_matrix(actual, predicted, labels, sample_weight=None, normalize=True)
    plt.clf()
    plt.cla()
    # plt.figure(figsize=(9,9))
    # plt.xticks(rotation=90)
    # plt.yticks(rotation=0)
    # cm = tf.math.confusion_matrix(actual, predicted)
    # ax = sns.heatmap(cm, annot=True, fmt='g')
    # sns.set(rc={'figure.figsize':(6, 6)})
    # sns.set(font_scale=1)
    # ax.set_title('Confusion matrix active sensing baseline')
    # ax.set_xlabel('Predicted Room')
    # ax.set_ylabel('Actual Room')
    # ax.xaxis.set_ticklabels(labels)
    # ax.yaxis.set_ticklabels(labels)

    ConfusionMatrixDisplay.from_predictions(y_true= actual, y_pred= predicted, display_labels= labels)

    plt.savefig("matrixbase" + ".png")
    plt.clf()
    plt.cla()

  def get_actual_predicted_labels(self, x_test, y_test): 
    actual = y_test
    predicted = self.model.predict(x_test)

    actual = tf.stack(actual, axis=0)
    predicted = tf.concat(predicted, axis=0)
    predicted = tf.argmax(predicted, axis=1)

    return actual, predicted

  def matrixEval(self, x_test, y_test):
    self.model.evaluate(x_test, y_test, return_dict=True)
    actual, predicted = self.get_actual_predicted_labels(x_test, y_test)
    self.plot_confusion_matrix(actual, predicted, ['master', 'livingrm', 'hallway',  'closet', 'bathrm', 'bedrm'], 'test')
