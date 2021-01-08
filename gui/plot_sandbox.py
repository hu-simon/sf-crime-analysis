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
    FigureCanvasQtAgg as FigureCanvas,
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


def _create_dropdown_box():
    geoframe = get_geometry()
    unique_districts = get_unique_entries(geoframe.district)
    polygons = create_polygon_dict(geoframe)

    class DistrictFigure(FigureCanvas):
        def __init__(self, parent=None, width=5, height=4, dpi=100):
            fig = Figure(figsize=(width, height), dpi=dpi)
            super(DistrictFigure, self).__init__(fig)

            self.axes = fig.add_subplot(111)
            self.plot_initial_figure()

        def plot_initial_figure(self):
            self.update_figure(unique_districts[0])

        def update_figure(self, district):
            self.plot(polygons[district])

        def plot(self, data):
            self.axes.clear()
            for item in data:
                self.axes.plot(*item.exterior.xy)
            self.draw_idle()

    class Window(qw.QDialog):
        def __init__(self, *args, **kwargs):
            super(Window, self).__init__(*args, **kwargs)
            self.setup_window()

            self.dropdown_groupbox = qw.QGroupBox()
            self.figure_groupbox = qw.QGroupBox()

            self.figure = FigureCanvas(self.figure_groupbox)

            self.create_dropdown_group()
            # self.create_initial_figure()

            self.main_layout = QVBoxLayout()
            self.main_layout.addWidget(self.dropdown_groupbox)
            self.main_layout.addWidget(self.figure_groupbox)
            self.setLayout(self.main_layout)

        def create_dropdown_group(self):
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

        def update_figure(self):
            current_district = self.dropdown_box.currentText()
            self.figure.update_figure(current_district)

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

        def setup_window(self, title=None, width=None, height=None, style=None):
            """Sets up the window options along with the style.
            
            Parameters
            ----------
            title : string, optional
                The title of the window, by default None. If None, then the title defaults to SF Crime Exploration.
            width : int, optional
                The width of the window, by default None. If None, then the width defaults to 650.
            height : int, optional
                The height of the window, by default None. If None, then the height defaults to 650.
            style : string, optional ("Fusion", "macintosh", "Windows")
                The UI style to be used, by default None. If None, then the style defaults to Fusion.

            """
            if title is None:
                title = "SF Crime Exploration"
            if width is None:
                width = 650
            if height is None:
                height = 650
            if style is None:
                style = "Fusion"

            self.setWindowTitle(title)
            self.resize(width, height)

            qw.QApplication.setStyle(qw.QStyleFactory.create(style))
            qw.QApplication.setPalette(qw.QApplication.style().standardPalette())

    app = qw.QApplication([])
    window = Window()
    window.show()
    app.exec_()


if __name__ == "__main__":
    _create_dropdown_box()
