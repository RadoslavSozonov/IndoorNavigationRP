from scipy.signal import spectrogram
from scipy.signal.windows import hann
from scipy.io.wavfile import read, write
from datetime import datetime
from database import LocalDatabase
from acoustic_classifier import AcousticClassifier
from sklearn.model_selection import train_test_split
from wifi_classifier import WifiClassifier
import cv2
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import time
import constants
import os
import json
 

matplotlib.use('Agg')
acoustic_model = AcousticClassifier()
db = LocalDatabase()
wifi_model = WifiClassifier("SVM")


def unique(list1):
 
    # initialize a null list
    unique_list = []
 
    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    return unique_list

def get_rooms_from_db():
    return db.get_buildings_with_rooms()

def find_first_chirp(arr, filename):
    # Scan at most the first interval for the first chirp
    sliced_arr = arr[:int(constants.interval_samples)]
    f, t, Sxx = spectrogram(sliced_arr, 44100, window=hann(256, sym=False))
    # Only handle high frequencies
    high_frequency_indices = np.where((f > constants.min_frequency) & (f < constants.max_frequency))
    Sxx_high = Sxx[high_frequency_indices]

    # Calculate the highest point of intensity to find the chirp
    end_of_chirps = np.argmax(Sxx_high, axis=1)

    counts = np.bincount(end_of_chirps)
    chirp_cut_off = np.argmax(counts)
    time_of_cut_off = t[chirp_cut_off]

    # f = f[high_frequency_indices]
    # t = t[chirp_cut_off:]
    # Sxx = Sxx[:,chirp_cut_off:]
    # # extract the maximum
    plt.pcolormesh(t, f, Sxx, shading='gouraud')
    plt.axvline(x=time_of_cut_off, color='r')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.savefig(filename)
    plt.clf()
    # Returns at which point in the sample is the center of the chirp
    return int(time_of_cut_off * constants.sample_rate )


def create_spectrogram(array, filename):
    f, t, Sxx = spectrogram(array, 44100, window=hann(256, sym=False))
    high_frequency_indices = np.where((f > constants.min_frequency) & (f < constants.max_frequency))
    f = f[high_frequency_indices]
    Sxx = Sxx[high_frequency_indices]

    # Plot the spectrogram and save it
    plt.pcolormesh(t, f, Sxx, shading='gouraud')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.savefig(filename)

    # Clear the plot
    plt.clf()

    # After saving, read the image and extract the graph from the figure
    time.sleep(0.1)
    rgb = cv2.imread(filename)
    rgb = rgb[59:428, 80:579]
    rgb = cv2.resize(rgb, (32, 5))
    not_rgb = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(filename, not_rgb)


def classify_single_echo(np_arr):
    today = datetime.now()
    classify_date = today.strftime("%b-%d-%Y-%H-%M-%S")
    meta_data_directory = './metadata/classify/'+ ""
    if not os.path.exists(meta_data_directory):
        # Create a new directory because it does not exist
        os.makedirs(meta_data_directory)
    
    
    first_chirp_offset = find_first_chirp(np_arr, meta_data_directory + classify_date + "-offset.png")
    np_arr = np_arr[int( first_chirp_offset + constants.chirp_radius_samples): int(constants.interval_samples + first_chirp_offset - constants.chirp_radius_samples)]
    filename = meta_data_directory + classify_date + "-echo.png"

    create_spectrogram(np_arr, filename)
    time.sleep(0.1)

    return acoustic_model.classify(db.get_grayscale_image(filename))


def create_training_set(np_arr, building_label, room_label, save_audio=True):
    today = datetime.now()
    classify_date = today.strftime("%b-%d-%Y-%H-%M-%S")

    # setup directories for data collection
    training_set_directory = './images/'+ str(building_label) + '/' + str(room_label)
    meta_data_directory = './metadata/'+ str(building_label) + '/' + str(room_label)
    if not os.path.exists(training_set_directory):
        # Create a new directory because it does not exist
        os.makedirs(training_set_directory)
    if not os.path.exists(meta_data_directory):
        # Create a new directory because it does not exist
        os.makedirs(meta_data_directory)
    # Save the audio as metadata
    if save_audio:
        write(meta_data_directory + '/audio-' + classify_date + '.wav', constants.sample_rate, np_arr.astype(np.int16))


    # Find the first chirp in the audio file and offset everything
    first_chirp_offset = find_first_chirp(np_arr, meta_data_directory + '/offset-' + classify_date + '.png')

    for i in range(constants.good_chirp_amount):
        # calculates the interval, and applied the chirp offset, to eliminate the emitted chirp and only process the echos
        start_rate = int(i * constants.interval_samples + first_chirp_offset + constants.chirp_radius_samples )
        # cuts out the ending chirp
        end_rate = int((i + 1) * constants.interval_samples + first_chirp_offset - constants.chirp_radius_samples  )
        sliced = np_arr[start_rate : end_rate]
        create_spectrogram(sliced, training_set_directory+ '/' + classify_date + '-' + str(i) + '.png')
    
def create_wifi_training_set(wifi_list, building_label, room_label):
    today = datetime.now()
    classify_date = today.strftime("%b-%d-%Y-%H-%M-%S")

    # setup directories for data collection
    training_set_directory = './wifi/'+ str(building_label) + '/' + str(room_label)
    meta_data_directory = './metadata/'+ str(building_label) + '/' + str(room_label)
    if not os.path.exists(training_set_directory):
        # Create a new directory because it does not exist
        os.makedirs(training_set_directory)
    if not os.path.exists(meta_data_directory):
        # Create a new directory because it does not exist
        os.makedirs(meta_data_directory)
    count = 0
    for wifi_fingerprint in wifi_list:
        # Serializing json
        json_object = json.dumps(wifi_fingerprint, indent=4)
        
        # Writing to sample.json
        with open(training_set_directory + "/" + str(count) +"-" + classify_date + ".json", "w") as outfile:
            outfile.write(json_object)
        count = 1 + count
from sklearn.metrics import accuracy_score
def test_classifiers(acoustic_test, acoustic_label, wifi_test, wifi_label):
    wifi_zip = list(zip(wifi_test, wifi_label))
    wifi_zip.sort(key=lambda x: x[1])
    acoustic_zip = list(zip(acoustic_test, acoustic_label))
    acoustic_zip.sort(key=lambda x: x[1])


    bins = np.bincount(wifi_label)
    print(bins)

    acoustic_combined = []
    wifi_combined = []
    for i in range(len(bins)):
        acoustic_data = [a for a in acoustic_zip if a[1] == i]
        wifi_data = [a for a in wifi_zip if a[1] == i]
        min_val = min(len(acoustic_data), len(wifi_data))
        acoustic_combined.extend(acoustic_data[:min_val])
        wifi_combined.extend(wifi_data[:min_val])
    new_wifi_test = [a[0] for a in wifi_combined]
    new_wifi_label = [a[1] for a in wifi_combined]
    new_acoustic_test = np.asarray([a[0] for a in acoustic_combined])
    new_acoustic_label = np.asarray([a[1] for a in acoustic_combined])


    wifi_pred = wifi_model.classify(new_wifi_test)
    print(accuracy_score(new_wifi_label, wifi_pred))
    print(acoustic_model.test_accuracy(new_acoustic_test, new_acoustic_label))

def train_classifiers(test_split=0.2): 
    images, image_labels, image_int_to_label = db.get_acoustic_training_set()
    wifis, wifi_labels, wifi_int_to_label = db.get_wifi_training_set()
    room_amount = db.get_room_amount()
    acoustic_dataset = train_test_split(images, image_labels, test_size=test_split, random_state=42)
    wifi_dataset = train_test_split(wifis, wifi_labels, test_size=test_split, random_state=42)
    acoustic_model.train(acoustic_dataset, image_int_to_label, room_amount)
    wifi_model.train(wifi_dataset, wifi_int_to_label, room_amount)

    test_classifiers(acoustic_dataset[1], acoustic_dataset[3], wifi_dataset[1], wifi_dataset[3])
        
def cross_corelation(arr, filename=None):

    samples = (np.sin(2 * np.pi * np.arange(params.duration * params.sample_rate) * params.frequency / params.sample_rate)).astype(np.float32)

    corr = signal.correlate(arr, samples, mode='same', method='fft')
    size = len(corr)

    started = False
    chirp_start = []
    chirp_end = []
    for i in range(size):
        if abs(corr[i]) > 100000 and not started:
            started = True
            chirp_start.append(i)
        if abs(corr[i]) < 100000 and started:
            chirp_end.append(i)
            started = False

    if len(chirp_start) == 0 or len(chirp_end) == 0:
        return 0, 0

    
    calculated_chirp_duration = (chirp_end[len(chirp_end) - 1] - chirp_start[0])
    chirp_midle = chirp_start[0] + calculated_chirp_duration / 2

    if filename is not None:
        plt.plot(np.arange(size) / params.sample_rate, corr)
        plt.savefig(filename)
        plt.clf()   


    return chirp_midle, calculated_chirp_duration

if __name__ == "__main__":

    train_classifiers()
    # today = datetime.now()
    # classify_date = today.strftime("%b-%d-%Y-%H-%M-%S")

    # # Save the audio as metadata
    # rate, np_arr = read('./audio-test.wav')

    # # Create the dataset
    # create_training_set(np_arr, "house", "upstairs", False)