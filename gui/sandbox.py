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


"""The checkable box works but you should probably modify it so that it works with what you expect.

Basically, the thing works but you probably don't understand why it works.

Another thing to consider: adding some sort of "Error Window" class that just takes a Error Message. 
"""


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


def _checkable_dropdown_box():
    geoframe = get_geometry()
    unique_districts = get_unique_entries(geoframe.district)
    polygons = create_polygon_dict(geoframe)

    class CheckableComboBox(qw.QComboBox):
        """ Drawn from https://gis.stackexchange.com/questions/350148/qcombobox-multiple-selection-pyqt5 """

        class Delegate(qw.QStyledItemDelegate):
            def sizeHint(self, option, index):
                size = super().sizeHint(option, index)
                size.setHeight(20)
                return size

        def __init__(self, *args, **kwargs):
            super(CheckableComboBox, self).__init__(*args, **kwargs)
            self.setEditable(True)
            self.lineEdit().setReadOnly(True)
            self.lineEdit().setAlignment(Qt.AlignCenter)
            palette = qw.QApplication.palette()
            palette.setBrush(QtGui.QPalette.Base, palette.button())
            self.lineEdit().setPalette(palette)

            self.setItemDelegate(CheckableComboBox.Delegate())
            self.model().dataChanged.connect(self.updateText)
            self.lineEdit().installEventFilter(self)
            self.closeOnLineEditClick = False
            self.view().viewport().installEventFilter(self)

        def resizeEvent(self, event):
            self.updateText()
            super().resizeEvent(event)

        def eventFilter(self, object, event):
            if object == self.lineEdit():
                if event.type() == QtCore.QEvent.MouseButtonRelease:
                    if self.closeOnLineEditClick:
                        self.hidePopup()
                    else:
                        self.showPopup()
                    return True
                return False

            if object == self.view().viewport():
                if event.type() == QtCore.QEvent.MouseButtonRelease:
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

            metrics = QtGui.QFontMetrics(self.lineEdit().font())
            elidedText = metrics.elidedText(
                text, Qt.ElideRight, self.lineEdit().width()
            )
            self.lineEdit().setText(elidedText)

        def addItem(self, text, data=None):
            item = QtGui.QStandardItem()
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
            self, title="SF Crime Exploration", width=650, height=650, style="Fusion",
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
            self.dropdown_box = CheckableComboBox()
            self.dropdown_box.addItems(unique_districts)

            self.plot_button = qw.QPushButton("Plot")
            self.plot_button.setMaximumWidth(80)
            self.clear_button = qw.QPushButton("Clear")
            self.clear_button.setMaximumWidth(80)

            group_layout = qw.QVBoxLayout()

            dropdown_layout = qw.QGridLayout()
            dropdown_layout.addWidget(self.district_label, 0, 0)
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
            # self.clear_button()
            # self.make_clickable(self.dropdown_box).connect(self.dropdown_box.showPopup)
            # self.make_clickable(self.line_edit).connect(self.dropdown_box.showPopup)

        def create_figure(self):
            self.figure_layout = qw.QVBoxLayout()
            self.figure_layout.addWidget(self.toolbar)
            self.figure_layout.addWidget(self.canvas)

            self.figure_groupbox = qw.QGroupBox()
            self.figure_groupbox.setLayout(self.figure_layout)

        def plot_initial_figure(self):
            self.update_figure()

        def update_figure(self):
            selected_districts = self.dropdown_box.currentData()

            self.axes.clear()
            self.axes.set_xticks([])
            self.axes.set_yticks([])
            for district in selected_districts:
                data = polygons[district]
                for entry in data:
                    self.axes.plot(*entry.exterior.xy, linewidth=0.5, color="blue")
                self.canvas.draw()

        def make_clickable(self, widget):
            class Filter(QtCore.QObject):
                clicked = QtCore.pyqtSignal()

                def eventFilter(self, obj, widget):
                    if obj == widget:
                        if event.type() == QtCore.QEvent.MouseButtonRelease:
                            if obj.rect().contains(event.pos()):
                                self.clicked.emit()
                                return True
                    return False

            filter = Filter(widget)
            widget.installEventFilter(filter)
            return filter.clicked

        def clear_checkbox(self):
            self.dropdown_box.clearData()
            self.axes.clear()
            self.axes.set_xticks([])
            self.axes.set_yticks([])
            self.canvas.draw()

    app = qw.QApplication([])
    window = Window()
    window.show()
    app.exec_()


if __name__ == "__main__":
    # _create_dropdown_box()
    _checkable_dropdown_box()
