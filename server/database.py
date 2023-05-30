import numpy as np
import os
from PIL import Image

class LocalDatabase:

    def get_grayscale_image(self, path):
        grey = Image.open(path)
        grey = np.asarray(grey)
        return grey

    def get_training_set(self):
        images = []
        labels = []
        int_to_label = []
        count = 0

        for building_label in next(os.walk('./images'))[1]:
            for room_label in next(os.walk('./images/' + building_label))[1]:
                # get all images for this room
                full_path = './images/' + building_label + '/' + room_label
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