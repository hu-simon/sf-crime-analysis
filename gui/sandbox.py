import os
import sys
import time
from tqdm import tqdm

import shapely
import numpy as np
import pandas as pd
import geopandas as gpd

from PyQt5 import QtGui, QtCore
import PyQt5.QtWidgets as qw
from PyQt5.QtCore import QDateTime, Qt, QTimer, QObject


def get_geometry(geodata_path=None):
    if geodata_path is None:
        geodata_path = "/Users/administrator/Documents/Projects/sf-crime-exploration/data/SFPD_District_Centroids.csv"
    geoframe = pd.read_csv(geodata_path)
    geoframe.geometry = geoframe.geometry.apply(shapely.wkt.loads)
    geoframe.centroid = geoframe.centroid.apply(shapely.wkt.loads)
    geoframe = gpd.GeoDataFrame(geoframe, geometry="geometry")

    return geoframe


def get_dataframe(data_path=None):
    if data_path is None:
        data_path = "/Users/administrator/Documents/Projects/sf-crime-exploration/data/SFPD_Crime_Data_Full.csv"
    dataframe = pd.read_csv(data_path)

    return dataframe


def _create_dropdown_box():
    geoframe = get_geometry()

    class Window(qw.QDialog):
        def __init__(self, *args, **kwargs):
            super(Window, self).__init__(*args, **kwargs)
            self.setWindowTitle("SF Crime Exploration")
            # self.resize(400, 300)

            self.create_dropbox()
            self.create_plot()

            self.main_layout = qw.QVBoxLayout()
            self.main_layout.addWidget(self.dropbox_groupbox)
            self.main_layout.addWidget(self.plot_groupbox)
            self.setLayout(self.main_layout)

        def create_dropbox(self):
            self.dropbox_groupbox = qw.QGroupBox()

            self.district_label = qw.QLabel("District")
            self.dropdown_box = qw.QComboBox()
            for district in geoframe.district:
                self.dropdown_box.addItem(str(district))
            self.dropdown_box.setEditable(True)
            self.line_edit = self.dropdown_box.lineEdit()
            self.line_edit.setAlignment(Qt.AlignCenter)
            self.line_edit.setReadOnly(True)
            # dropdown_box.setStyleSheet("QComboBox {" "  padding-left: 20px" "}")

            group_layout = qw.QGridLayout()
            group_layout.addWidget(self.district_label, 0, 0)
            group_layout.addWidget(self.dropdown_box, 0, 1)
            group_layout.setColumnStretch(1, 2)
            self.dropbox_groupbox.setLayout(group_layout)

            self.make_clickable(self.dropdown_box).connect(self.dropdown_box.showPopup)
            self.make_clickable(self.line_edit).connect(self.dropdown_box.showPopup)

        def create_plot(self):
            self.plot_groupbox = qw.QGroupBox()

        def make_clickable(self, widget):
            class Filter(QtCore.QObject):
                clicked = QtCore.pyqtSignal()

                def eventFilter(self, obj, event):
                    if obj == widget:
                        if event.type() == QtCore.QEvent.MouseButtonRelease:
                            if obj.rect().contains(event.pos()):
                                self.clicked.emit()
                                return True
                    return False

            filter = Filter(widget)
            widget.installEventFilter(filter)
            return filter.clicked

    app = qw.QApplication([])
    window = Window()
    window.show()
    app.exec_()


if __name__ == "__main__":
    _create_dropdown_box()
