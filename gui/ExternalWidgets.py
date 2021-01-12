"""Python file containing external widgets used for the San Francisco Crime Exploration project.

NOTE Documentation is not finished.
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
    dataframe = pd.read_csv(data_path)

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
    for index, entry in geoframe.iterrows():
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


class DistrictPlot(qw.QDialog):
    def __init__(self, *args, **kwargs):
        super(DistrictPlot, self).__init__(*args, **kwargs)

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
        if geodata_path is None:
            geodata_path = "/Users/administrator/Documents/Projects/sf-crime-exploration/data/SFPD_District_Centroids.csv"
        geoframe = pd.read_csv(geodata_path)
        geoframe.geometry = geoframe.geometry.apply(shapely.wkt.loads)
        geoframe.centroid = geoframe.centroid.apply(shapely.wkt.loads)
        self.geoframe = gpd.GeoDataFrame()

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

    def create_figure_group(self):
        pass

    def plot_initial_figure(self):
        pass
