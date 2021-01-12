"""Python file containing external widgets used for the San Francisco Crime Exploration project.

NOTE Documentation is not finished.
NOTE Error in logic when new options are selected. Also need to figure out how to make the computation faster.
NOTE Division by zero when the user unchecks everything and then clicks the plot button. Should perform a check so that this does not happen!
"""

import os
import sys
import time

import shapely
import numpy as np
import pandas as pd
import geopandas as gpd

import PyQt5.QtWidgets as qw
from PyQt5 import QtGui as qg, QtCore as qc
from PyQt5.QtCore import Qt, QTimer, QObject

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)


def get_geometric_dataframe(geodata_path=None):
    """Loads geometric data containing the districts and their associated Polygons.
    
    Parameters
    ----------
    geodata_path : str, optional
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


def get_crime_dataframe(crimedata_path=None):
    """Loads the San Francisco Crime data as a Pandas DataFrame instance.
    
    Parameters
    ----------
    crimedata_path : str, optional
        The absolute path to a .csv file containing the crime data, by default None. If None, then the default path is used.

    Returns
    -------
    dataframe : pandas.DataFrame instance
        A Pandas DataFrame containing the San Francisco Crime data.

    """
    if crimedata_path is None:
        crimedata_path = "/Users/administrator/Documents/Projects/sf-crime-exploration/data/SFPD_Crime_Data_Full.csv"
    dataframe = pd.read_csv(crimedata_path)

    return dataframe


def get_district_polygons(geodata):
    """Returns a dictionary containing the Shapely polygons and their associated policing districts.

    Parameters
    ----------
    geometric_data : geopandas.GeoDataFrame instance
        GeoDataFrame containing the geometric data containing the districts and their associated Polygons.
    
    Returns
    -------
    polygons : dict
        Dictionary containing the Shapely polygons and their associated policing districts.

    """
    polygons = {}
    for index, entry in geodata.iterrows():
        if entry.district not in polygons.keys():
            polygons[entry.district] = []
        polygons[entry.district].append(entry.geometry)

    return polygons


class Delegate(qw.QStyledItemDelegate):
    """Implementation drawn from 
    https://gis.stackexchange.com/questions/350148/qcombobox-multiple-selection-pyqt5

    """

    def __init__(self):
        super(Delegate, self).__init__()

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(20)
        return size


class CheckableComboBox(qw.QComboBox):
    """Implementation drawn from 
    https://gis.stackexchange.com/questions/350148/qcombobox-multiple-selection-pyqt5
    
    """

    def __init__(self, *args, **kwargs):
        super(CheckableComboBox, self).__init__(*args, **kwargs)

        self.setEditable(True)

        self.lineEdit().setReadOnly(True)
        self.lineEdit().setAlignment(Qt.AlignCenter)
        palette = qw.QApplication.palette()
        palette.setBrush(qg.QPalette.Base, palette.button())
        self.lineEdit().setPalette(palette)

        self.setItemDelegate(Delegate())
        self.model().dataChanged.connect(self.updateText)
        self.lineEdit().installEventFilter(self)
        self.closeOnLineEditClick = False
        self.view().viewport().installEventFilter(self)

    def resizeEvent(self, event):
        self.updateText()
        super().resizeEvent(event)

    def eventFilter(self, obj, event):
        if obj == self.lineEdit():
            if event.type() == qc.QEvent.MouseButtonRelease:
                if self.closeOnLineEditClick:
                    self.hidePopup()
                else:
                    self.showPopup()
                return True
            return False

        if obj == self.view().viewport():
            if event.type() == qc.QEvent.MouseButtonRelease:
                index = self.view().indexAt(event.pos())
                item = self.model().item(index.row())

                if item.checkState() == Qt.Checked:
                    item.setCheckState(Qt.Unchecked)
                else:
                    item.setCheckState(Qt.Checked)
                return True
        return False

    def showPopup(self):
        super().showPopup()
        self.closeOnLineEditClick = True

    def hidePopup(self):
        super().hidePopup()
        self.startTimer(100)
        self.updateText()

    def timerEvent(self, event):
        self.killTimer(event.timerId())
        self.closeOnLineEditClick = False

    def updateText(self):
        texts = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.Checked:
                texts.append(self.model().item(i).text())
        text = ", ".join(texts)

        metrics = qg.QFontMetrics(self.lineEdit().font())
        elidedText = metrics.elidedText(text, Qt.ElideRight, self.lineEdit().width())
        self.lineEdit().setText(elidedText)

    def addItem(self, text, data=None):
        item = qg.QStandardItem()
        item.setText(text)
        if data is None:
            item.setData(text)
        else:
            item.setData(data)
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        item.setData(Qt.Unchecked, Qt.CheckStateRole)
        self.model().appendRow(item)

    def addItems(self, texts, datalist=None):
        for i, text in enumerate(texts):
            try:
                data = datalist[i]
            except (TypeError, IndexError):
                data = None
            self.addItem(text, data)

    def currentData(self):
        res = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.Checked:
                res.append(self.model().item(i).data())
        return res

    def clearData(self):
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.Checked:
                self.model().item(i).setCheckState(Qt.Unchecked)


class CategoryPlot(qw.QDialog):
    def __init__(self, *args, **kwargs):
        super(CategoryPlot, self).__init__(*args, **kwargs)

        self.load_data()

        self.setup_window()
        self.setup_figure()

        self.create_dropdown_group()
        self.create_figure_group()
        self.plot_initial_figure()

        self.main_layout = qw.QVBoxLayout()
        self.main_layout.addWidget(self.dropdown_groupbox)
        self.main_layout.addWidget(self.figure_groupbox)
        self.setLayout(self.main_layout)

    def load_data(self, geodata_path=None, crimedata_path=None):
        """Loads in geometric and crime data as a Pandas DataFrame.
        
        Parameters
        ----------
        geodata_path : str, optional
            Absolute path to the location containing the geometric data, by default None. If None, then the default directory is used.
        crimedata_path : str, optional
            Absolute path to the location containing the crime data, by default None. If None, then the default directory is used.

        """
        # Load the geometric data.
        geom_data = get_geometric_dataframe()
        self.district_polygons = get_district_polygons(geom_data)

        # Load the crime data.
        crime_data = get_crime_dataframe()
        self.crime_categories = list(crime_data["Category"].unique())
        self.district_categories = list(crime_data["Police District"].unique())
        self.get_crimes_by_district(crime_data)

    def get_crimes_by_district(self, crime_data):
        """Returns a dictionary containing key-value pairs of districts and their associated distribution of crimes, stored in a dictionary.
        
        Parameters
        ----------
        crime_data : pandas.DataFrame
            A Pandas DataFrame containing the San Francisco Crime data.
        
        """
        self.crimes_by_district = {}
        for district in self.district_categories:
            district_dataframe = crime_data[crime_data["Police District"] == district]
            crime_distribution = {}
            for category in self.crime_categories:
                crime_distribution[category] = len(
                    district_dataframe[district_dataframe["Category"] == category]
                )
            self.crimes_by_district[district] = crime_distribution

    def setup_window(
        self,
        title="San Francisco Crime Exploration",
        width=650,
        height=650,
        style="Fusion",
    ):
        """Sets up the window using the provided options.
        
        Parameters
        ----------
        title : str, optional
            The title of the window, by default "San Francisco Crime Exploration".
        width : int, optional
            The width of the window in pixels, by default 650.
        height : int, optional
            The height of the window in pixels, by default 650.
        style : str, optional
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

        # Remove the spines
        self.axes.spines["top"].set_visible(False)
        self.axes.spines["bottom"].set_visible(False)
        self.axes.spines["left"].set_visible(False)
        self.axes.spines["right"].set_visible(False)

    def create_dropdown_group(self):
        """Sets up the checkable combo box group, containing the checkable dropdown box, a plot button, and a clear button.

        """
        self.dropdown_groupbox = qw.QGroupBox()

        self.crime_label = qw.QLabel("Crime")
        self.dropdown_box = CheckableComboBox()
        self.dropdown_box.addItems(self.crime_categories)

        self.plot_button = qw.QPushButton("Plot")
        self.plot_button.setMaximumWidth(80)
        self.clear_button = qw.QPushButton("Clear")
        self.clear_button.setMaximumWidth(80)

        group_layout = qw.QVBoxLayout()

        dropdown_layout = qw.QGridLayout()
        dropdown_layout.addWidget(self.crime_label, 0, 0)
        dropdown_layout.addWidget(self.dropdown_box, 0, 1)
        dropdown_layout.setColumnStretch(1, 2)

        button_layout = qw.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.plot_button, 0, Qt.AlignRight)
        button_layout.addWidget(self.clear_button, 0, Qt.AlignRight)

        group_layout.addLayout(dropdown_layout)
        group_layout.addSpacing(15)
        group_layout.addLayout(button_layout)
        self.dropdown_groupbox.setLayout(group_layout)

        self.plot_button.clicked.connect(self.update_figure)
        self.clear_button.clicked.connect(self.clear_checkbox)

    def create_figure_group(self):
        group_layout = qw.QVBoxLayout()
        group_layout.addWidget(self.toolbar)
        group_layout.addWidget(self.canvas)

        self.figure_groupbox = qw.QGroupBox()
        self.figure_groupbox.setLayout(group_layout)

    def plot_initial_figure(self):
        self.plot_all_districts()

    def plot_all_districts(self):
        for district in self.district_polygons:
            for polygon in self.district_polygons[district]:
                self.axes.plot(*polygon.exterior.xy, linewidth=0.5, color="blue")
        self.axes.set_xticks([])
        self.axes.set_yticks([])
        self.canvas.draw()

    def update_figure(self):
        self.clear_axes()
        checked_categories = self.dropdown_box.currentData()

        # Compute the weights for each of the districts, based on the chosen categories.
        district_weights = {}
        total_number_crimes = 0
        for district in self.district_categories:
            if district not in district_weights.keys():
                district_weights[district] = 0
            for category in checked_categories:
                district_weights[district] += self.crimes_by_district[district][
                    category
                ]
                total_number_crimes += self.crimes_by_district[district][category]

        # Normalize them to get the weights.
        for district in self.district_categories:
            district_weights[district] /= total_number_crimes

        # Plot all of the districts.
        self.clear_axes()
        for district in self.district_polygons:
            for polygon in self.district_polygons[district]:
                # self.axes.plot(*polygon.exterior.xy, color="blue", linewidth=0.5)
                self.axes.fill(
                    *polygon.exterior.xy, color="red", alpha=district_weights[district]
                )
        self.axes.set_xticks([])
        self.axes.set_yticks([])
        self.canvas.draw()

    def clear_checkbox(self):
        self.dropdown_box.clearData()
        self.clear_axes()
        self.canvas.draw()

    def clear_axes(self):
        self.axes.clear()
        self.plot_all_districts()
