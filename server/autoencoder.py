import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf

from keras import layers, losses
from keras.models import Model, Sequential

class Denoise(Model):
  def __init__(self):
    super(Denoise, self).__init__()
    self.encoder = tf.keras.Sequential([
      layers.Conv2D(1, (4, 4), activation='relu', input_shape=(5, 32, 1), padding="same", strides=(1,1)),
      layers.Conv2D(16, (4, 4), activation='relu', input_shape=(5, 32, 16), padding="same", strides=(1,1))])

    self.decoder = tf.keras.Sequential([
      layers.Conv2DTranspose(16, (4, 4), activation='relu', input_shape=(5, 32, 16), padding="same", strides=(1,1)),
      layers.Conv2DTranspose(1, (4, 4), activation='relu', input_shape=(5, 32, 1), padding="same", strides=(1,1)),
      layers.Conv2D(1, kernel_size=(4, 4), activation='sigmoid', padding='same')])

  def call(self, x):
    encoded = self.encoder(x)
    decoded = self.decoder(encoded)
    return decoded

autoencoder = Denoise()