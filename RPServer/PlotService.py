from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt


class PlotService:
    def __init__(self):
        pass

    def confusion_matrix_creator(self, name, y_act, y_pred, class_names):
        cm = confusion_matrix(y_act, y_pred)
        ax = plt.subplot()
        sns.heatmap(cm, annot=True, ax=ax, fmt='g');
        ax.set_xlabel('Predicted', fontsize=20)
        ax.xaxis.set_label_position('bottom')
        plt.xticks(rotation=90)
        ax.xaxis.set_ticklabels(class_names, fontsize=10)
        ax.xaxis.tick_bottom()
        ax.set_ylabel('True', fontsize=20)
        ax.yaxis.set_ticklabels(class_names, fontsize=10)
        plt.yticks(rotation=0)
        plt.title(name, fontsize=20)
        plt.savefig("confusion_matrices/" + name + ".png")
        plt.clf()

    def line_plot_creator(self, name, data):
        plt.clf()
        for element in data:
            plt.plot(element["x"], element["y"], color=element["color"], label=element["label"])
        plt.legend(loc="upper left")
        plt.savefig("plots/" + name + ".png")
        plt.clf()