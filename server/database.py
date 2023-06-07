import numpy as np
import os
from PIL import Image
import json


def unique(list1):
 
    # initialize a null list
    unique_list = []
 
    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    return unique_list

class LocalDatabase:

    def get_grayscale_image(self, path):
        grey = Image.open(path)
        grey = np.asarray(grey)
        return grey

    def get_acoustic_training_set(self, time="night"):
        images = []
        labels = []
        int_to_label = []
        count = 0

        for building_label in next(os.walk('./images'))[1]:
            for room_label in next(os.walk('./images/' + building_label))[1]:
                # get all images for this room
                full_path = './images/' + building_label + '/' + room_label + "/" + time
                full_label = building_label + ': ' + room_label
                files = (file for file in os.listdir(full_path) 
                        if os.path.isfile(os.path.join(full_path, file)))
                for sample in files:
                    # get the image, create a label, and then add it to the list
                    grey = Image.open(full_path + '/' +sample)
                    grey = np.asarray(grey)
                    images.append(grey)
                    labels.append(count)
                int_to_label.append(full_label)
                count = count + 1

        images = np.asarray(images)
        labels = np.asarray(labels)
        return (images, labels, int_to_label)


    def create_wifi_fingerprint(self, wifi_list, wifi_unique_BSSID):
        # print("wifi unique size:" + str(len(wifi_unique_BSSID)))
        # print("wifi list size:" + str(len(wifi_list)))

        size = len(wifi_unique_BSSID)
        np_arr = np.zeros(size)
        for i in range(size):
            BSSID = wifi_unique_BSSID[i]
            np_arr[i] = next((x["level"] for x in wifi_list if x["BSSID"] == BSSID), 0)
        return np_arr
    def get_unique_wifi_BSSID(self, time="night"):
        wifi_BSSID = []
        for building_label in next(os.walk('./wifi'))[1]:
            for room_label in next(os.walk('./wifi/' + building_label))[1]:
                # get all wifi fingerprints for this room
                full_path = './wifi/' + building_label + '/' + room_label + "/" + time
                full_label = building_label + ': ' + room_label
                files = (file for file in os.listdir(full_path) 
                        if os.path.isfile(os.path.join(full_path, file)))
                for sample in files:
                    with open(full_path + '/' +sample, 'r') as openfile:
                        # Reading from json file
                        wifi_list = json.load(openfile)
                        for wifi in wifi_list["list"]:
                            wifi_BSSID.append(wifi["BSSID"])
        
        return unique(wifi_BSSID)

    def get_wifi_training_set(self, time="night"):
        wifi_fingerprints = []
        labels = []
        int_to_label = []
        count = 0
        wifi_unique_BSSID = self.get_unique_wifi_BSSID()

        for building_label in next(os.walk('./wifi'))[1]:
            for room_label in next(os.walk('./wifi/' + building_label))[1]:
                # get all wifi fingerprints for this room
                full_path = './wifi/' + building_label + '/' + room_label + "/" + time
                full_label = building_label + ': ' + room_label
                files = (file for file in os.listdir(full_path) 
                        if os.path.isfile(os.path.join(full_path, file)))
                for sample in files:
                    with open(full_path + '/' +sample, 'r') as openfile:
                    
                        # Reading from json file
                        wifi_list = json.load(openfile)
                        wifi_fingerprint = self.create_wifi_fingerprint(wifi_list["list"], wifi_unique_BSSID)
                        wifi_fingerprints.append(wifi_fingerprint)
                        labels.append(count)
                int_to_label.append(full_label)
                count = count + 1
        wifi_fingerprints = np.asarray(wifi_fingerprints)
            
        labels = np.asarray(labels)
        return (wifi_fingerprints, labels, int_to_label)

    def get_room_amount(self):
        count = 0
        for building_label in next(os.walk('./images'))[1]:
            for room_label in next(os.walk('./images/' + building_label))[1]:
                count = count + 1
        return count
    def get_buildings_with_rooms(self):
        buildings = {}
        room_list = []
        for building_label in next(os.walk('./images'))[1]:
            for room_label in next(os.walk('./images/' + building_label))[1]:
                # add room to the list
                room_list.append(room_label)
            # Add all the rooms to the appropriate building
            buildings.update({building_label: room_list})
            room_list = []
        return buildings

if __name__ == "__main__":
    db = LocalDatabase()

    db.get_wifi_training_set()