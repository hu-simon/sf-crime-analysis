import os
import sys
import time
from tqdm import tqdm

import shapely
import numpy as np
import pandas as pd
import geopandas as gpd

import PyQt5.QtWidgets as qw
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QDateTime, Qt, QTimer, QObject

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)


def get_geometry(geodata_path=None):
    """Loads geometric data containing the districts and their associated Polygons.
    
    Parameters
    ----------
    geodata_path : string, optional
        The absolute path to a .csv file containing the geometric data, by default None. If None, then the default path is used.
    
    Returns
    -------
    geoframe : geopandas.GeoDataFrame instance
        A GeoDataFrame containing the geometric data containing the districts and their associated Polygons.

    """
    if geodata_path is None:
        geodata_path = "/Users/administrator/Documents/Projects/sf-crime-exploration/data/SFPD_District_Centroids.csv"
    geoframe = pd.read_csv(geodata_path)
    geoframe.geometry = geoframe.geometry.apply(shapely.wkt.loads)
    geoframe.centroid = geoframe.centroid.apply(shapely.wkt.loads)
    geoframe = gpd.GeoDataFrame(geoframe, geometry="geometry")

    return geoframe


def get_dataframe(data_path=None):
    """Loads the San Francisco Crime data as a Pandas DataFrame instance.
    
    Parameters
    ----------
    data_path : string, optional
        The absolute path to a .csv file containing the data, by default None. If None, then the default path is used.
    
    Returns
    -------
    dataframe : pandas.DataFrame instance
        A Pandas DataFrame containing the San Francisco Crime data. 

    """
    if data_path is None:
        data_path = "/Users/administrator/Documents/Projects/sf-crime-exploration/data/SFPD_Crime_Data_Full.csv"
    dataframe = pd.read_csv(data_path)

    return dataframe


def get_unique_entries(entries):
    """Returns a list of unique entries from a list.
    
    Parameters
    ----------
    entries : list
        List containing potentially non-unique entries.
    
    Returns
    -------
    unique_entries : list
        List containing unique entries from ``entries``.

    """
    unique_entries = list()
    for entry in entries:
        if entry not in unique_entries:
            unique_entries.append(entry)
        else:
            continue

    return unique_entries


def create_polygon_dict(geoframe):
    """Returns a dictionary mapping a district to a Shapely Polygon.
    
    Parameters
    ----------
    geoframe : geopandas.GeoDataFrame
        A GeoDataFrame containing the geometric data containing the districts and their associated Polygons.
    
    Returns
    -------
    polygons_dict : dictionary (string, shapely.geometry.Polygon)
        A dictionary containing district-Polygon pairs for each of the unique districts.

    """
    polygons_dict = {}
    for index, row in geoframe.iterrows():
        if row.district not in polygons_dict.keys():
            polygons_dict[row.district] = []
        polygons_dict[row.district].append(row.geometry)

    return polygons_dict


"""
def _create_dropdown_box():
    geoframe = get_geometry()
    unique_districts = get_unique_entries(geoframe.district)
    polygons = create_polygon_dict(geoframe)

    class Window(qw.QDialog):
        def __init__(self, *args, **kwargs):
            super(Window, self).__init__(*args, **kwargs)
            self.setWindowTitle("SF Crime Exploration")
            self.resize(650, 650)

            qw.QApplication.setStyle(qw.QStyleFactory.create("Fusion"))
            qw.QApplication.setPalette(qw.QApplication.style().standardPalette())

            self.figure = Figure()
            self.ax = self.figure.add_subplot(111)
            self.canvas = FigureCanvas(self.figure)
            self.toolbar = NavigationToolbar(self.canvas, self)

            self.plot_groupbox = qw.QGroupBox()

            self.create_dropbox()
            self.create_plot()

            self.plot_groupbox.setLayout(self.plotgroup_layout)

            self.main_layout = qw.QVBoxLayout()
            self.main_layout.addWidget(self.dropbox_groupbox)
            self.main_layout.addWidget(self.plot_groupbox)
            self.setLayout(self.main_layout)

        def create_dropbox(self):
            self.dropbox_groupbox = qw.QGroupBox()

            self.district_label = qw.QLabel("District")
            self.plot_button = qw.QPushButton("Plot")
            self.plot_button.setMaximumWidth(80)
            self.dropdown_box = qw.QComboBox()
            for district in unique_districts:
                self.dropdown_box.addItem(str(district))
            self.dropdown_box.setEditable(True)
            self.line_edit = self.dropdown_box.lineEdit()
            self.line_edit.setAlignment(Qt.AlignCenter)
            self.line_edit.setReadOnly(True)

            main_layout = qw.QVBoxLayout()

            group_layout = qw.QGridLayout()
            group_layout.addWidget(self.district_label, 0, 0)
            group_layout.addWidget(self.dropdown_box, 0, 1)
            group_layout.setColumnStretch(1, 2)

            button_layout = qw.QHBoxLayout()
            button_layout.addWidget(self.plot_button, 0, Qt.AlignRight)

            main_layout.addLayout(group_layout)
            main_layout.setSpacing(15)
            main_layout.addLayout(button_layout)

            self.dropbox_groupbox.setLayout(main_layout)

            self.plot_button.clicked.connect(self.create_plot)
            self.make_clickable(self.dropdown_box).connect(self.dropdown_box.showPopup)
            self.make_clickable(self.line_edit).connect(self.dropdown_box.showPopup)

        def create_plot(self):
            current_district = self.dropdown_box.currentText()
            data = polygons[current_district]

            self.ax.clear()
            for entry in data:
                self.ax.plot(*entry.exterior.xy)
            # self.canvas.draw()
            # self.canvas.flush_events()

            self.plotgroup_layout = qw.QVBoxLayout()
            self.plotgroup_layout.addWidget(self.toolbar)
            self.plotgroup_layout.addWidget(self.canvas)

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
"""


def _create_dropdown_box():
    geoframe = get_geometry()
    unique_districts = get_unique_entries(geoframe.district)
    polygons = create_polygon_dict(geoframe)

    class Window(qw.QDialog):
        def __init__(self, *args, **kwargs):
            super(Window, self).__init__(*args, **kwargs)

            self.setup_window()
            self.setup_figure()

            self.create_dropdown_box()
            self.create_figure()
            self.plot_initial_figure()

            self.main_layout = qw.QVBoxLayout()
            self.main_layout.addWidget(self.dropdown_groupbox)
            self.main_layout.addWidget(self.figure_groupbox)
            self.setLayout(self.main_layout)

        def setup_window(
            self, title="SF Crime Exploration", width=650, height=650, style="Fusion"
        ):
            """Sets up the window options along with the style.
            
            Parameters
            ----------
            title : string, optional
                The title of the window, by default "SF Crime Exploration"
            width : int, optional
                The width of the window, by default 650.
            height : int, optional
                The height of the window, by default 650.
            style : string, optional ("Fusion", "macintosh", "Windows")
                The UI style to be used, by default "Fusion".

            """
            self.setWindowTitle(title)
            self.resize(width, height)

            qw.QApplication.setStyle(qw.QStyleFactory.create(style))
            qw.QApplication.setPalette(qw.QApplication.style().standardPalette())

        def setup_figure(self):
            """Sets up the objects used for plotting figures."""
            self.figure = Figure()
            self.axes = self.figure.add_subplot(111)
            self.canvas = FigureCanvas(self.figure)
            self.toolbar = NavigationToolbar(self.canvas, self)

            # Remove splines
            self.axes.spines["top"].set_visible(False)
            self.axes.spines["bottom"].set_visible(False)
            self.axes.spines["left"].set_visible(False)
            self.axes.spines["right"].set_visible(False)

        def create_dropdown_box(self):
            self.dropdown_groupbox = qw.QGroupBox()

            self.district_label = qw.QLabel("District")
            self.dropdown_box = qw.QComboBox()
            for district in unique_districts:
                self.dropdown_box.addItem(district)
            self.dropdown_box.setEditable(True)
            self.line_edit = self.dropdown_box.lineEdit()
            self.line_edit.setAlignment(Qt.AlignCenter)
            self.line_edit.setReadOnly(True)

            self.plot_button = qw.QPushButton("Plot")
            self.plot_button.setMaximumWidth(80)

            group_layout = qw.QVBoxLayout()

            dropdown_layout = qw.QGridLayout()
            dropdown_layout.addWidget(self.district_label, 0, 0)
            dropdown_layout.addWidget(self.dropdown_box, 0, 1)
            dropdown_layout.setColumnStretch(1, 2)

            button_layout = qw.QHBoxLayout()
            button_layout.addWidget(self.plot_button, 0, Qt.AlignRight)

            group_layout.addLayout(dropdown_layout)
            group_layout.setSpacing(15)
            group_layout.addLayout(button_layout)
            self.dropdown_groupbox.setLayout(group_layout)

            # Events
            self.plot_button.clicked.connect(self.update_figure)
            self.make_clickable(self.dropdown_box).connect(self.dropdown_box.showPopup)
            self.make_clickable(self.line_edit).connect(self.dropdown_box.showPopup)

        def create_figure(self):
            self.figure_layout = qw.QVBoxLayout()
            self.figure_layout.addWidget(self.toolbar)
            self.figure_layout.addWidget(self.canvas)

            self.figure_groupbox = qw.QGroupBox()
            self.figure_groupbox.setLayout(self.figure_layout)

        def plot_initial_figure(self):
            self.update_figure()

        def update_figure(self):
            current_district = self.dropdown_box.currentText()
            data = polygons[current_district]

            self.axes.clear()
            self.axes.set_xticks([])
            self.axes.set_yticks([])
            for entry in data:
                self.axes.plot(*entry.exterior.xy)
            self.canvas.draw()

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
