"""Driver for the ExternalWidgets.py testing.
"""

import os
import sys
import time
from tqdm import tqdm

import ExternalWidgets
import PyQt5.QtWidgets as qw

app = qw.QApplication([])
window = ExternalWidgets.CategoryPlot()
window.show()
app.exec_()
