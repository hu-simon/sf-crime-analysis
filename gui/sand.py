import math
import numpy as np
from PyQt5 import QtGui, QtCore, QtWidgets

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class UsersPerCountryAndPlatformBar(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, fig)

        self.axes = fig.add_subplot(111)
        self.compute_initial_figure()

    def compute_initial_figure(self):

        A_B = [
            ["Afghanistan", "Albania", "Algeria", "American Samoa", "Angola"],
            [1, 9, 7, 1, 1],
            [1, 7, 2, 0, 1],
            [0, 4, 3, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]
        C_F = [
            ["Cambodia", "Canada", "Chile", "China", "Colombia"],
            [13, 189, 12, 5, 10],
            [5, 115, 6, 64, 7],
            [1, 11, 1, 2, 4],
            [2, 12, 0, 2, 0],
            [2, 5, 0, 0, 0],
        ]
        self.data = {"A_B": A_B, "C_F": C_F}
        self.updatefig("A_B")

    def updatefig(self, text):
        self.plot(self.data[text])

    def plot(self, X_Y):
        self.axes.clear()
        summedX_Y = []
        for i in range(len(X_Y[0])):
            summedX_Y.append(X_Y[1][i] + X_Y[2][i] + X_Y[3][i] + X_Y[4][i] + X_Y[5][i])

        def roundup(x):
            return int(math.ceil(x / 10.0)) * 10

        N = len(X_Y[0])
        ind = np.arange(N)
        width = 0.75
        colors = [
            "yellowgreen",
            "paleturquoise",
            "royalblue",
            "lightsteelblue",
            "firebrick",
        ]

        print([x + y for x, y in zip(X_Y[1], X_Y[2])])
        print([x + y + z for x, y, z in zip(X_Y[1], X_Y[2], X_Y[3])])
        print([x + y + z + i for x, y, z, i in zip(X_Y[1], X_Y[2], X_Y[3], X_Y[4])])

        p1 = self.axes.bar(ind, X_Y[1], width, color=colors[0])
        p2 = self.axes.bar(ind, X_Y[2], width, bottom=X_Y[1], color=colors[1])
        p3 = self.axes.bar(
            ind,
            X_Y[3],
            width,
            bottom=[x + y for x, y in zip(X_Y[1], X_Y[2])],
            color=colors[2],
        )
        p4 = self.axes.bar(
            ind,
            X_Y[4],
            width,
            bottom=[x + y + z for x, y, z in zip(X_Y[1], X_Y[2], X_Y[3])],
            color=colors[3],
        )
        p5 = self.axes.bar(
            ind,
            X_Y[5],
            width,
            bottom=[
                x + y + z + i for x, y, z, i in zip(X_Y[1], X_Y[2], X_Y[3], X_Y[4])
            ],
            color=colors[4],
        )

        self.axes.set_ylabel("Count")
        self.axes.set_title("Users Per Country And Platform")
        self.axes.set_xticks(ind)
        # self.axes.set_xticklabels(countrylabels, fontsize = 8)
        self.axes.set_yticklabels(
            np.arange(0, max(summedX_Y), roundup(max(summedX_Y) / 10))
        )
        self.axes.legend(
            (p1[0], p2[0], p3[0], p4[0], p5[0]),
            ("Android", "iOS", "Windows", "OS X", "WebGL"),
        )
        self.draw_idle()


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):

        self.main_widget = QtGui.QWidget(MainWindow)
        l = QtGui.QVBoxLayout(self.main_widget)

        self.main_widget.setFocus()
        MainWindow.setCentralWidget(self.main_widget)

        self.UPCP = UsersPerCountryAndPlatformBar(
            self.main_widget, width=10, height=5, dpi=100
        )

        comboBox = QtGui.QComboBox(MainWindow)
        comboBox.addItem("A_B")
        comboBox.addItem("C_F")
        comboBox.activated[str].connect(self.UPCP.updatefig)
        l.addWidget(comboBox)
        l.addWidget(self.UPCP)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
