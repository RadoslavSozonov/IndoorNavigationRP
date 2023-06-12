import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, accuracy_score

def create_confusion_matrix(labels, predictions, int_to_label, accuracy, name):

    cm = confusion_matrix(int_to_label[labels], int_to_label[predictions], labels=int_to_label)
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_title(name + ", accuracy=" + str(accuracy))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=int_to_label)
    disp.plot(ax=ax, xticks_rotation="vertical", cmap=plt.cm.Blues)
    plt.savefig("./metadata/accuracy/" + name +"_confusion_matrix.png", bbox_inches="tight")
    plt.clf()

