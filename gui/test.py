import os
import sys
import time
from tqdm import tqdm

import PyQt5.QtWidgets as qw
from PyQt5.QtCore import QDateTime, Qt, QTimer
from fbs_runtime.application_context.PyQt5 import ApplicationContext


class WidgetGallery(qw.QDialog):
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)

        self.original_palette = qw.QApplication.palette()

        style_combo_box = qw.QComboBox()
        style_combo_box.addItems(qw.QStyleFactory.keys())

        style_label = qw.QLabel("&Style:")
        style_label.setBuddy(style_combo_box)

        self.use_style_palette_checkbox = qw.QCheckBox("&Use style's standard palette")
        self.use_style_palette_checkbox.setChecked(True)

        disabled_widgets_checkbox = qw.QCheckBox("&Disable Widgets")

        self.create_top_left_groupbox()
        self.create_top_right_groupbox()
        self.create_bottom_left_tabwidget()
        self.create_bottom_right_groupbox()
        self.create_progress_bar()

        style_combo_box.activated[str].connect(self.change_style)
        self.use_style_palette_checkbox.toggled.connect(self.change_palette)
        disabled_widgets_checkbox.toggled.connect(self.top_left_groupbox.setDisabled)
        disabled_widgets_checkbox.toggled.connect(self.top_right_groupbox.setDisabled)
        disabled_widgets_checkbox.toggled.connect(
            self.bottom_left_tabwidget.setDisabled
        )
        disabled_widgets_checkbox.toggled.connect(
            self.bottom_right_groupbox.setDisabled
        )

        top_layout = qw.QHBoxLayout()
        top_layout.addWidget(style_label)
        top_layout.addWidget(style_combo_box)
        top_layout.addStretch(1)
        top_layout.addWidget(self.use_style_palette_checkbox)
        top_layout.addWidget(disabled_widgets_checkbox)

        main_layout = qw.QGridLayout()
        main_layout.addLayout(top_layout, 0, 0, 1, 2)
        main_layout.addWidget(self.top_left_groupbox, 1, 0)
        main_layout.addWidget(self.top_right_groupbox, 1, 1)
        main_layout.addWidget(self.bottom_left_tabwidget, 2, 0)
        main_layout.addWidget(self.bottom_right_groupbox, 2, 1)
        main_layout.addWidget(self.progress_bar, 3, 0, 1, 2)
        main_layout.setRowStretch(1, 1)
        main_layout.setRowStretch(2, 1)
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 1)
        self.setLayout(main_layout)

        self.setWindowTitle("Styles")
        self.change_style("macintosh")

    def change_style(self, style_name):
        qw.QApplication.setStyle(qw.QStyleFactory.create(style_name))
        self.change_palette()

    def change_palette(self):
        if self.use_style_palette_checkbox.isChecked():
            qw.QApplication.setPalette(qw.QApplication.style().standardPalette())
        else:
            qw.QApplication.setPalette(self.original_palette)

    def advance_progress_bar(self):
        current_value = self.progress_bar.value()
        maximum_value = self.progress_bar.maximum()
        self.progress_bar.setValue(
            current_value + (maximum_value - current_value) / 100
        )

    def create_top_left_groupbox(self):
        self.top_left_groupbox = qw.QGroupBox("Group 1")

        radio_button_1 = qw.QRadioButton("Radio Button 1")
        radio_button_2 = qw.QRadioButton("Radio Button 2")
        radio_button_3 = qw.QRadioButton("Radio Button 3")
        radio_button_1.setChecked(True)

        check_box = qw.QCheckBox("Tri-State Check Box")
        check_box.setTristate(True)
        check_box.setCheckState(Qt.PartiallyChecked)

        layout = qw.QVBoxLayout()
        layout.addWidget(radio_button_1)
        layout.addWidget(radio_button_2)
        layout.addWidget(radio_button_3)
        layout.addWidget(check_box)
        layout.addStretch(1)
        self.top_left_groupbox.setLayout(layout)

    def create_top_right_groupbox(self):
        self.top_right_groupbox = qw.QGroupBox("Group 2")

        default_pushbutton = qw.QPushButton("Default Push Button")
        default_pushbutton.setDefault(True)

        toggle_pushbutton = qw.QPushButton("Toggle Push Button")
        toggle_pushbutton.setCheckable(True)
        toggle_pushbutton.setChecked(True)

        flat_pushbutton = qw.QPushButton("Flat Push Button")
        flat_pushbutton.setFlat(True)

        layout = qw.QVBoxLayout()
        layout.addWidget(default_pushbutton)
        layout.addWidget(toggle_pushbutton)
        layout.addWidget(flat_pushbutton)
        layout.addStretch(1)
        self.top_right_groupbox.setLayout(layout)

    def create_bottom_left_tabwidget(self):
        self.bottom_left_tabwidget = qw.QTabWidget()
        self.bottom_left_tabwidget.setSizePolicy(
            qw.QSizePolicy.Preferred, qw.QSizePolicy.Ignored
        )

        tab1 = qw.QWidget()
        table_widget = qw.QTableWidget(10, 10)

        tab1_hbox = qw.QHBoxLayout()
        tab1_hbox.setContentsMargins(5, 5, 5, 5)
        tab1_hbox.addWidget(table_widget)
        tab1.setLayout(tab1_hbox)

        tab2 = qw.QWidget()
        text_edit = qw.QTextEdit()

        text_edit.setPlainText(
            "Twinkle, twinkle, little star, \n" "Power is I squared R\n"
        )

        tab2_hbox = qw.QHBoxLayout()
        tab2_hbox.setContentsMargins(5, 5, 5, 5)
        tab2_hbox.addWidget(text_edit)
        tab2.setLayout(tab2_hbox)

        self.bottom_left_tabwidget.addTab(tab1, "&Table")
        self.bottom_left_tabwidget.addTab(tab2, "Text &Edit")

    def create_bottom_right_groupbox(self):
        self.bottom_right_groupbox = qw.QGroupBox("Group 3")
        self.bottom_right_groupbox.setCheckable(True)
        self.bottom_right_groupbox.setChecked(True)

        line_edit = qw.QLineEdit("s3cRe7")
        line_edit.setEchoMode(qw.QLineEdit.Password)

        spin_box = qw.QSpinBox(self.bottom_right_groupbox)
        spin_box.setValue(50)

        date_time_edit = qw.QDateTimeEdit(self.bottom_right_groupbox)
        date_time_edit.setDateTime(QDateTime.currentDateTime())

        slider = qw.QSlider(Qt.Horizontal, self.bottom_right_groupbox)
        slider.setValue(40)

        scroll_bar = qw.QScrollBar(Qt.Horizontal, self.bottom_right_groupbox)
        scroll_bar.setValue(60)

        dial = qw.QDial(self.bottom_right_groupbox)
        dial.setValue(30)
        dial.setNotchesVisible(True)

        layout = qw.QGridLayout()
        layout.addWidget(line_edit, 0, 0, 1, 2)
        layout.addWidget(spin_box, 1, 0, 1, 2)
        layout.addWidget(date_time_edit, 2, 0, 1, 2)
        layout.addWidget(slider, 3, 0)
        layout.addWidget(scroll_bar, 4, 0)
        layout.addWidget(dial, 3, 1, 2, 1)
        layout.setRowStretch(5, 1)
        self.bottom_right_groupbox.setLayout(layout)

    def create_progress_bar(self):
        self.progress_bar = qw.QProgressBar()
        self.progress_bar.setRange(0, 10000)
        self.progress_bar.setValue(0)

        timer = QTimer(self)
        timer.timeout.connect(self.advance_progress_bar)
        timer.start(1000)


if __name__ == "__main__":
    """ fbs does not work for this version of Python
    app_context = ApplicationContext()
    gallery = WidgetGallery()
    gallery.show()
    sys.exit(app_context.app.exec_())
    """
    app = qw.QApplication(sys.argv)
    gallery = WidgetGallery()
    gallery.show()
    sys.exit(app.exec_())
