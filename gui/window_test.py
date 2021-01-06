import os
import sys
import time
from tqdm import tqdm

from PyQt5 import QtCore, QtGui, QtWidgets as qw
from PyQt5.QtCore import QDateTime, Qt, QTimer


import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg,
    NavigationToolbar2QT as NavigationToolbar,
)

import gmaps
import shapely
import numpy as np
import pandas as pd
import geopandas as gpd


def initiate_gmaps(key_path):
    """Performs authentication for using the Google Maps API.
    
    Parameters
    ----------
    key_path : string
        String containing the absolute path to the api key.

    """
    try:
        with open(key_path) as f:
            api_key = f.readline()
            f.close()
        gmaps.configure(api_key=api_key)
        print("Successfully authenticated the API key.")
    except:
        print("Failed to authenticate the API key.")


class MPLCanvas(FigureCanvasQTAgg):
    """Class that wraps over a Matplotlib Figure Canvas.
    
    """

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """Instantiates a new MPLCanvas object.
        
        Parameters
        ----------
        parent : [type], optional
            [description], by default None
        width : int, optional
            [description], by default 5
        height : int, optional
            [description], by default 4
        dpi : int, optional
            [description], by default 100

        TODO documentation

        """
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MPLCanvas, self).__init__(fig)


class MainWindow(qw.QDialog):
    """Class representing the entire app.
    
    """

    def __init__(self, *args, **kwargs):
        """Instantiates a new MainWindow instance.

        Parameters
        ----------
        args : arguments
        kwargs : keyword arguments
        
        TODO documentation

        """
        super(MainWindow, self).__init__(*args, **kwargs)

    def create_category_dropbox(self):
        """Creates a dropbox allowing the user to select the category of crimes that they want to include. 

        NOTE we can use the QFontComboBox widget to create a drop-down button.
        """


def load_geometric_data(geometric_path):
    """Loads geometric data into a Pandas GeoDataFrame.
    
    Parameters
    ----------
    geometric_path : [type]
        [description]
    
    TODO documentation

    """
    geoframe = pd.read_csv(geometric_path)
    geoframe.geometry = geoframe.geometry.apply(shapely.wkt.loads)
    geoframe.centroid = geoframe.centroid.apply(shapely.wky.loads)
    geoframe = gpd.GeoDataFrame(geoframe, geometry="geometry")
    polyframe = geoframe.geometry

    return geoframe, polyframe


if __name__ == "__main__":
    pass
