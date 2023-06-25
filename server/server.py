from flask import Flask, request 
import firebase_admin
from firebase_admin import credentials, firestore
from scipy.io.wavfile import write
from scipy.signal import spectrogram
from scipy.signal.windows import hann
from autoencoder import Denoise
from cnn import CNN
from datetime import datetime

from sklearn.utils import shuffle
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from keras import layers, losses, preprocessing

import cv2
import random
import tensorflow as tf
import os, glob
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


APP = Flask(__name__)

cred = credentials.Certificate('key.json')
app = firebase_admin.initialize_app(cred)
db = firestore.client()

mode = 'passive'

sample_rate = 44100
chirp_amount = 8
# amount of chirps that are ignored, since some of the last chirps dont work
chirp_error_amount = 4




def create_spectrogram(array, filename, passive):
    #print(array)
    #print(array.shape)
    f, t, Sxx = spectrogram(array, 44100, window=hann(256, sym=False), noverlap=128)
    #f, t, Sxx = spectrogram(array, 44100)
    if(passive):
        index = np.where((f >= 0) & (f <= 1000))
        filename = "passive/" + filename
    else:
        index = np.where((f >= 19500) & (f <= 20500))
        filename = "active/" + filename
    #print(f)
    #breakpoint = 0
    #for freq in f:
    #    if(freq > 1000):
    #        break
    #    breakpoint += 1
    filtered = Sxx[index[0][0]:index[0][-1]]
    # print(filtered.shape)
    plt.pcolormesh(t, f[index[0][0]:index[0][-1]], filtered, shading='auto')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.savefig(filename + ".png")
    plt.clf()
    plt.cla()
    #print(filtered.shape)
    #print("filter above")
    #np.save(filename, filtered)



@APP.route('/get_rooms', methods=['GET'])
def get_rooms():
    room_list = []
    response_body = {}
    collections = db.collections()
    for collection in collections:
        for document in collection.list_documents():
            room_list.append(document.get().to_dict()["room"])
        response_body.update({collection.id: room_list})
        room_list = []

    return response_body


@APP.route('/add_room', methods=['POST'])
def add_room():
    room_data = request.json
    room_label = room_data['room_label']
    building_label = room_data['building_label']
    room_audio = room_data['audio']
    passive = room_data['passive']
    chirp_amount = room_data['amount']
    interval = room_data['interval']
    interval_rate = interval*sample_rate

    threshold = 3000
    if(passive):
        threshold = 1

    counter = 0
    np_arr = np.asarray(room_audio, dtype=np.int16)
    print(np_arr[0])
    chirp_sample_offset = (np.where(np_arr[0] > threshold))[0][0]
    if(passive):
        chirp_start = chirp_sample_offset
    else:
        chirp_max = np.argmax(np_arr[0, chirp_sample_offset:(chirp_sample_offset+4000)])
        print(chirp_max)
        chirp_start = chirp_sample_offset + chirp_max - 44
        print(chirp_start)

    for i in range(chirp_amount - chirp_error_amount):
        start_rate = int(i * interval_rate + chirp_start)
        sliced = np_arr[0,(start_rate+(110)):(int(start_rate + interval_rate))]
        create_spectrogram(sliced, building_label + '/' + room_label + '/track' + datetime.now().strftime('%d-%m-%Y - %H-%M-%S') + ' - '  + str(counter) , passive)
        counter +=1

    return 'OK'


@APP.route('/classify', methods=['POST'])
def classify_room():
    audio = request.files['audio']
    #TODO: run the clasifier
    result = 'room_1'
    return result

@APP.route('/validate', methods=['POST'])
def validate():
    

    testspec = []
    testlabel = []

    testset = request.json
    pathTest = mode + '/' + testset + '/'

    rooms = ['masterbedroom', 'livingroom', 'hallway',  'closet', 'bathroom', 'myroom']
    count = 0

    for room in rooms:

        for filename in glob.glob(os.path.join(pathTest + room, '*.npy')):
            spectrum = np.load(filename)
            testspec.append(spectrum)
            testlabel.append(count)
        count += 1

    shuffle(testspec, testlabel, random_state=16)

    x_new = np.asarray(testspec)
    y_new = np.asarray(testlabel)

    cnn = CNN()
    cnn.load(mode)
    cnn.matrixEval(x_new, y_new)

    return "done"



@APP.route('/train', methods=['POST'])
def train_model():
    spectrograms = []
    labels = []
    
    trainset = 'std' 
    testsize = 60
    if(mode == 'active'):
        testsize = 600

    pathTrain = mode + '/' + trainset + '/'
    rooms = ['masterbedroom', 'livingroom', 'hallway',  'closet', 'bathroom', 'myroom']

    count = 0
    for room in rooms:
        for filename in glob.glob(os.path.join(pathTrain + room, '*.npy')):
            spectrum = np.load(filename)
            spectrograms.append(spectrum)
            labels.append(count)

        count += 1

    shuffle(spectrograms, labels, random_state=32)

    np_arr = np.asarray(spectrograms)
    label_arr = np.asarray(labels)
    x_train, x_test, y_train, y_test = train_test_split(np_arr, label_arr, test_size=testsize, shuffle=True, random_state=42)

    cnn = CNN()
    if(mode == 'active'):
        cnn.trainActive(x_train, x_test, y_train, y_test)
    else:
        cnn.trainPassive(x_train, x_test, y_train, y_test)
    
    cnn.save(mode)

    return "OK"


if __name__ == '__main__':
    APP.run(host='0.0.0.0', debug=True)

def autoEncoderMix(np_arr, label_arr):
    indexes = np.argsort(y_train)
    x_train = np.array(x_train)[indexes]
    y_train = np.array(y_train)[indexes]
    x_train2 = []
    temp = []
    currentLabel = y_train[0]
    count = 0
    for y in y_train:
        if(y == currentLabel):
            temp.append(x_train[count])
        else:
            currentLabel = y
            random.shuffle(temp)
            x_train2 = x_train2 + temp
            temp = []
            temp.append(x_train[count])
        count += 1

    random.shuffle(temp)
    x_train2 = x_train2 + temp

    x_train2 = np.asarray(x_train2)
    print(x_train.shape)
    print(x_train2.shape)



    x_trainAE, x_testAE, y_trainAE, y_testAE = train_test_split(x_train, x_train2, test_size=300, random_state=42)


    autoencoder = Denoise()
    autoencoder.compile(optimizer='adam', loss=losses.MeanSquaredError())
    autoencoder.fit(x_trainAE, y_trainAE,
                 epochs=50,
                 shuffle=True,
                 validation_data=(x_testAE, y_testAE))
    
    x_train, y_train = shuffle(x_train, y_train, random_state=42)
    x_train = autoencoder.call(np.array(x_train)).numpy()[0].reshape((5, 32))
    return x_train, y_train

def dataAug():
    datagen = preprocessing.image.ImageDataGenerator(width_shift_range=0.2, fill_mode='wrap')
    datagen.fit(x_train)
    print(x_train)
    train_gen=datagen.flow(x_train, y_train, batch_size=3000)
    
    x_train, y_train = next(train_gen)
    
    validation_data=datagen.flow(x_train, y_train,
        batch_size=400, subset='validation')
    
    return x_train, y_train, validation_data

def plotSpec(spec):
    print(np.array(spec).shape)
    plt.pcolormesh(spec[0], shading='flat')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.savefig("beforetest" + ".png")
    plt.clf

    #cv2.imwrite("decodetest.png", x_train[0])
    # print(np.array(x_train).shape)
    # plt.pcolormesh(x_train, shading='flat')
    #plt.ylabel('Frequency [Hz]')
    #plt.xlabel('Time [sec]')
    # plt.savefig("decodetest" + ".png")
    # plt.clf

