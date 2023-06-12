from scipy.signal import spectrogram
from scipy.signal.windows import hann
from scipy.io.wavfile import read, write
from datetime import datetime
from database import LocalDatabase
from acoustic_classifier import AcousticClassifier
from sklearn.model_selection import train_test_split
from wifi_classifier import WifiClassifier
from sklearn.metrics import accuracy_score
import cv2
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import time
import constants
import os
import json
from sorcery import dict_of
from combined_classifier import WeightedAverage, TwoStep, wifi_top_k, wifi_top_k_test_accuracy, acoustic_top_k, acoustic_top_k_test_accuracy, wifi_top_k_to_string, acoustic_top_k_to_string
 
matplotlib.use('Agg')
db = LocalDatabase()
acoustic_model = AcousticClassifier()
wifi_model = WifiClassifier()
weighted_model = WeightedAverage(acoustic_model, wifi_model, [])
two_step_model = TwoStep(acoustic_model, wifi_model, [])


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
    plt.pcolormesh(t, f, Sxx, shading='nearest')
    plt.axvline(x=time_of_cut_off, color='r')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.savefig(filename, bbox_inches="tight")
    plt.clf()
    # Returns at which point in the sample is the center of the chirp
    return int(time_of_cut_off * constants.sample_rate )


def create_spectrogram(array, filename):
    f, t, Sxx = spectrogram(array, 44100, window=hann(256, sym=False))
    high_frequency_indices = np.where((f > constants.min_frequency) & (f < constants.max_frequency))
    f = f[high_frequency_indices]
    Sxx = Sxx[high_frequency_indices]

    # Plot the spectrogram and save it
    plt.pcolormesh(t, f, Sxx, shading='nearest')
    plt.axis('off')
    plt.savefig(filename, bbox_inches="tight", pad_inches=0)

    # Clear the plot
    plt.clf()

    # After saving, read the image and extract the graph from the figure
    time.sleep(0.1)
    rgb = cv2.imread(filename)
    # rgb = rgb[59:428, 80:579]
    rgb = cv2.resize(rgb, (32, 5))
    not_rgb = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
    scale = 255/np.max(not_rgb)
    not_rgb = (not_rgb * scale).astype(np.uint8)
    cv2.imwrite(filename, not_rgb)


def multi_classify(np_arr, wifi_list):
    if acoustic_model.model_trained == False:
        train_classifiers()
    int_to_label = wifi_model.get_int_to_label()
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
    
    acoustic_sample = db.get_grayscale_image(filename)
    wifi_sample = db.create_wifi_fingerprint(wifi_list)
    acoustic_prediction = [acoustic_model.classify(acoustic_sample)]
    wifi_prediction = [wifi_model.classify(wifi_sample)]
    
    weighted_average_prediction = [weighted_model.classify(acoustic_sample, wifi_sample)]
    two_step_prediction = [two_step_model.classify(acoustic_sample, wifi_sample)]
    wifi_top_k_prediction = wifi_top_k_to_string(wifi_model, constants.top_k, wifi_sample)
    acoustic_top_k_prediction = acoustic_top_k_to_string(acoustic_model, constants.top_k, acoustic_sample)
    prediction_object = dict_of(
        acoustic_prediction,
        wifi_prediction,
        weighted_average_prediction,
        two_step_prediction,
        wifi_top_k_prediction,
        acoustic_top_k_prediction
    )
    return prediction_object


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

def test_classifiers(acoustic_test_set, acoustic_test_labels, wifi_test_set, wifi_test_labels, acoustic_training_dataset, wifi_training_dataset):
    wifi_accuracy = wifi_model.test_accuracy(wifi_test_set,wifi_test_labels)
    acoustic_accuracy = acoustic_model.test_accuracy(acoustic_test_set, acoustic_test_labels)

    weighted_model.set_int_to_label(acoustic_model.get_int_to_label())
    two_step_model.set_int_to_label(acoustic_model.get_int_to_label())

    weighted_accuracy = weighted_model.train(acoustic_training_dataset, wifi_training_dataset, (acoustic_test_set, acoustic_test_labels), (wifi_test_set, wifi_test_labels))
    two_step_accuracy = two_step_model.train(acoustic_training_dataset, wifi_training_dataset, (acoustic_test_set, acoustic_test_labels), (wifi_test_set, wifi_test_labels))
    wifi_top_k_accuracy = wifi_top_k_test_accuracy(wifi_model, constants.top_k, wifi_test_set, wifi_test_labels)
    acoustic_top_k_accuracy = acoustic_top_k_test_accuracy(acoustic_model, constants.top_k, acoustic_test_set, wifi_test_labels)
    print("WIFI MODEL ACCURACY: " + str(wifi_accuracy))
    print("ACOUSTIC MODEL ACCURACY: " + str(acoustic_accuracy))
    print("WEIGHTED AVERAGE ACCURACY: " + str(weighted_accuracy))
    print("TWO STEP LOCALIZATION ACCURACY: " + str(two_step_accuracy))
    print("ACOUSTIC TOP K ACCURACY: " + str(acoustic_top_k_accuracy))
    print("WIFI TOP K ACCURACY: " + str(wifi_top_k_accuracy))

def combine_dataset(wifi_set, wifi_labels, acoustic_set, acoustic_labels):

    wifi_zip = list(zip(wifi_set, wifi_labels))
    wifi_zip.sort(key=lambda x: x[1])
    acoustic_zip = list(zip(acoustic_set, acoustic_labels))
    acoustic_zip.sort(key=lambda x: x[1])

    bins = np.bincount(wifi_labels)

    acoustic_combined = []
    wifi_combined = []
    for i in range(len(bins)):
        acoustic_data = [a for a in acoustic_zip if a[1] == i]
        wifi_data = [a for a in wifi_zip if a[1] == i]
        min_val = min(len(acoustic_data), len(wifi_data))
        acoustic_combined.extend(acoustic_data[:min_val])
        wifi_combined.extend(wifi_data[:min_val])
    new_wifi_set = [a[0] for a in wifi_combined]
    new_wifi_labels = [a[1] for a in wifi_combined]
    new_acoustic_set = np.asarray([a[0] for a in acoustic_combined])
    new_acoustic_labels = np.asarray([a[1] for a in acoustic_combined])
    return new_wifi_set, new_wifi_labels, new_acoustic_set, new_acoustic_labels


def get_combined_dataset():
    images, image_labels, acoustic_int_to_label = db.get_acoustic_training_set()
    wifis, wifi_labels, wifi_int_to_label = db.get_wifi_training_set()
    acoustic_training_set, acoustic_temp_set, acoustic_training_labels , acoustic_temp_labels = train_test_split(images, image_labels, test_size=0.2, random_state=42)
    wifi_training_set, wifi_test_set, wifi_training_labels, wifi_test_labels = train_test_split(wifis, wifi_labels, test_size=0.4, random_state=42)

    acoustic_validation_set, acoustic_test_set, acoustic_validation_labels, acoustic_test_labels = train_test_split(acoustic_temp_set, acoustic_temp_labels, test_size=0.5, random_state=42)

    new_wifi_training_set, new_wifi_training_labels, new_acoustic_training_set, new_acoustic_training_labels = combine_dataset(wifi_training_set, wifi_training_labels, acoustic_training_set, acoustic_training_labels)
    new_wifi_test_set, new_wifi_test_labels, new_acoustic_test_set, new_acoustic_test_labels = combine_dataset(wifi_test_set, wifi_test_labels, acoustic_test_set, acoustic_test_labels)

    acoustic_dataset = (acoustic_training_set, acoustic_training_labels, acoustic_validation_set, acoustic_validation_labels, new_acoustic_test_set, new_acoustic_test_labels)
    wifi_dataset = (wifi_training_set, wifi_training_labels, new_wifi_test_set, new_wifi_test_labels)
    acoustic_training_dataset = (new_acoustic_training_set, new_acoustic_training_labels)
    wifi_training_dataset = (new_wifi_training_set, new_wifi_training_labels)
    return acoustic_dataset, wifi_dataset, acoustic_int_to_label, wifi_int_to_label, acoustic_training_dataset, wifi_training_dataset
    

def train_classifiers(test_split=0.2): 
    room_amount = db.get_room_amount()
    acoustic_dataset, wifi_dataset, acoustic_int_to_label, wifi_int_to_label, acoustic_training_dataset, wifi_training_dataset = get_combined_dataset()

    acoustic_model.train(acoustic_dataset, acoustic_int_to_label, room_amount, "best_acoustic.h5") # 
    wifi_model.train(wifi_dataset, wifi_int_to_label, room_amount, "./models/best_wifi.sav") # 

    test_classifiers(acoustic_dataset[4], acoustic_dataset[5], wifi_dataset[2], wifi_dataset[3], acoustic_training_dataset, wifi_training_dataset)

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


    # for room_label in next(os.walk('./metadata/pulse/'))[1]:
    #     full_path = './metadata/pulse' + '/' + room_label
    #     files = (file for file in os.listdir(full_path) 
    #             if os.path.isfile(os.path.join(full_path, file)))
    #     for sample in files:
    #         # get the image, create a label, and then add it to the list
    #         rate, np_arr = read(full_path + '/' +sample)
    #         create_training_set(np_arr, "pulse", room_label)
    train_classifiers()
    # today = datetime.now()
    # classify_date = today.strftime("%b-%d-%Y-%H-%M-%S")

    # # Save the audio as metadata
    # rate, np_arr = read('./audio-test.wav')

    # # Create the dataset
    # create_training_set(np_arr, "house", "upstairs", False)