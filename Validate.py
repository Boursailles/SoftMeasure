import os
import matplotlib.pyplot as plt
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from time import sleep, time
from statistics import mean 
import numpy as np
import math
import matplotlib.colors as mcolors
import matplotlib.cm as cm
from Save import *
from Interface import *



###############################################################################
# This program is working with Interface.py file as parent, and Plot_GUI.py and Save.py files as children for SoftMeasure.
# It contains useful code allowing to launch proper measurement.
###############################################################################



class Valid:
    def __init__(self, devices):
        """Class called when "okay" button is clicked.

        Args:
            devices (dict): Dictionnary containing all devices used in SoftMeasure.
        """
        self.devices = devices
        # Directory path for measurement files recording. Default to None. 
        self.path = None
        # Error handling.
        sys.excepthook = self.error_handler

    def widget(self):
        """Display of plot frame widgets.
        """
        self.save = Save()
        self.okay = QPushButton('Okay')
        self.okay.clicked.connect(self.okay_event)

        self.cancel = QPushButton('Close')
        self.cancel.clicked.connect(QCoreApplication.instance().quit)

        self.box = QGroupBox('')
        self.box.setFlat(True)

        self.progressbar = QProgressBar()
        self.progressbar.setVisible(False)
        retainsize = self.progressbar.sizePolicy()
        retainsize.setRetainSizeWhenHidden(True)
        self.progressbar.setSizePolicy(retainsize)

        self.estimated_time = QLabel('Estimated time:')
        self.estimated_time.setVisible(False)
        retainsize = self.estimated_time.sizePolicy()
        retainsize.setRetainSizeWhenHidden(True)
        self.estimated_time.setSizePolicy(retainsize)

        self.display_time = QLabel('')
        self.display_time.setVisible(False)
        retainsize = self.display_time.sizePolicy()
        retainsize.setRetainSizeWhenHidden(True)
        self.display_time.setSizePolicy(retainsize)

        self.emergency = QPushButton()
        self.emergency.setGeometry(200, 200, 100, 100)
        self.emergency.setStyleSheet( "*{border-image: url(Emergency_button.png);} :hover{ border-image: url(Emergency_button_hovered.png);}")
        self.emergency.setFixedWidth(40)
        self.emergency.setFixedHeight(40)
        self.emergency.setVisible(False)
        retainsize = self.emergency.sizePolicy()
        retainsize.setRetainSizeWhenHidden(True)
        self.emergency.setSizePolicy(retainsize)
        self.cancel.clicked.connect(self.off())

        layout = QGridLayout()

        layout.addWidget(self.save.box, 0, 0, 1, 2)
        layout.addWidget(self.okay, 0, 2)
        layout.addWidget(self.cancel, 0, 3)
        layout.addWidget(self.progressbar, 1, 0)
        layout.addWidget(self.estimated_time, 1, 1)
        layout.addWidget(self.display_time, 1, 2)
        layout.addWidget(self.emergency, 1, 3, alignment=Qt.AlignCenter)

        self.box.setLayout(layout)

    def okay_event(self):
        """Event method when the "okay" button is clicked.
        """
        self.path = self.save.pathEdit.text()
        
        self.save_params()
        self.folder()
        self.connection()
        self.initialization()
        self.meas_record()

    def save_params(self):
        """Save last filled QWidget parameters.
        """
        for value in self.devices.values():
            value.save_params()

    def folder(self):
        """Create folder, subfolders and txt files for futur measurements to the chosen file path and instrument(s).
        """
        # Creating parent folder.
        try:
            for value in self.devices.values():
                value.file()
        # A modifier, à mettre dans la gestion générale des erreurs qui déconnectera les machines.
        except FileNotFoundError as e:
            QMessageBox.about(self.parent, 'Warning', e)
            return

    def connection(self):
        """Connection to the chosen instrument(s).
        """
        # Measurement method for the VNA device depends if the SM one is used or not.
        VNA_step = self.devices['vna'].connection(self.devices['sm'].box.isChecked())
        # Measurement method for the SM device depends if the VNA one is used (and hence need its step number) or not.
        self.devices['sm'].connection(VNA_step)
        
        # If the current to apply is considered as to high by the user, it can be stopped.
        current_to_apply = self.devices['ps'].connection()
        if current_to_apply != 0:
            return self.off()
        
        self.devices['gm'].connection()

    def initialization(self):
        """Initialization to the chosen instrument(s).
        """
        for value in self.devices.values():
            value.initialization()

    def measurement(self):
        """Launching measurement.
        """
        # Measurement class.
        self.meas = Measure_QT(self.devices)

        """
        # Connecting signals of the measurement class.
        self.meas.msg_error.connect(self.msg_error)
        self.meas.off.connect(self.off)
        self.emergency.clicked.connect(self.meas.bool_switch)"""

        # Creating measurement QThread.
        self.meas_thread = QThread()
        self.meas.moveToThread(self.meas_thread)
        self.meas_thread.started.connect(self.meas.meas)
        self.meas.finished.connect(self.meas_thread.exit)

        # Launch measurement and progressbar.
        self.meas_thread.start()
        self.launch_progressbar()
                
    def off(self):
        """Turn off instrument(s).
        """
        try:
            self.meas.finished()
        except NameError:
            pass
        
        for value in self.devices.values():
            value.off()
        # Voir quoi faire de ça
        self.okay.setEnabled(True)
    
    def error_handler(self, exctype, value, traceback):
        """All kind of errors are handled, and call "off" method.

        Args:
            exctype (str): Type of the exception raised.
            value (str): Instance of the exception raised.
            traceback (str): Traceback of the exception raised
        """
        # Stop all instruments.
        self.off()
        # Create a message box for the error.
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText('An error occured!')
        msg.setInformativeText(f'<span style="color: red;"><b>{exctype}:<b></span> {value}')
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    '''
    def launch_progressbar(self):
        """Display of the progressbar.
        """
        self.okay.setDisabled(True)
        self.time = 0

        # Adding of the time delay due to the SM measurement.
        if self.parent.sm.box.isChecked():
            self.time = float(self.parent.sm.meas_time.text()) + 0.1

            if self.parent.vna.box.isChecked():
                self.time *= float(self.parent.vna.nb_step.text())

        # Total time delay of iterated measurement due to the PS sweep.
        if self.parent.ps.box.isChecked():
            ps_sleep = 0.5
            ps_epsilon = 4e-4
            I_start = float(self.parent.ps.I_start.text())
            I_stop = float(self.parent.ps.I_stop.text())
            I_nb_step = float(self.parent.ps.nb_step.text())
            current_step = abs(I_start - I_stop)/I_nb_step
            self.time = int((self.time + (math.log2(current_step/ps_epsilon) + 1)*ps_sleep)*I_nb_step + math.log2(abs(I_start - I_stop)/ps_epsilon)*ps_sleep) + 1

        else:
            self.time = int(self.time) + 1


        if self.time != 1:
            # Setting of the progressbar parameters.
            self.progressbar.setMinimum(0)
            self.progressbar.setMaximum(self.time)

            self.progressbar.setValue(0)
            self.display_time.setText('')
            self.progressbar.setVisible(True)
            self.estimated_time.setVisible(True)
            self.display_time.setVisible(True)
            self.emergency.setVisible(True)

            # Creating a QThread for the progressbar
            self.pb_thread = QThread()
            self.pb_qt = Progressbar_QT(self.time)

            self.pb_qt.moveToThread(self.pb_thread)
            self.pb_thread.started.connect(self.pb_qt.loading)
            
            self.pb_qt.change_value.connect(self.set_progressbar_val)

            self.pb_qt.finished.connect(self.pb_thread.exit)
            self.pb_qt.finished.connect(self.end_progressbar)

            self.pb_thread.start()


    def set_progressbar_val(self, val):
        """
        Showing remaining time of the set of measurement and bounded updating of the progressbar.

        ---------
        Parameter:
        val: int
            Measurement time in sec.
        """

        # Updating progressbar.
        self.progressbar.setValue(val)

        # Computing of the time in hour.
        hour = str((self.time - val)//3600)
        if len(hour) == 1:
            hour = '0' + hour

        # Computing of the remaining time in minute (after substracting hour time).
        min = str((self.time - val)%3600//60)
        if len(min) == 1:
            min = '0' + min

        # Computing of the remaining time in second (after substracting hour and minute times).
        sec = str((self.time - val)%3600%60)
        if len(sec) == 1:
            sec = '0' + sec

        # Display of the remaining time.
        self.display_time.setText(hour + ':' + min + ':' + sec)


    def end_progressbar(self):
        """"
        Hidding of the progressbar when the measurement is done.
        """

        self.progressbar.setVisible(False)
        self.estimated_time.setVisible(False)
        self.display_time.setVisible(False)
        self.emergency.setVisible(False)
        self.pb_qt.bool = False
        self.display_time.setText('')
        self.progressbar.setValue(0)

    '''



class Progressbar_QT(QObject):
    change_value = pyqtSignal(int)
    finished = pyqtSignal()
    def __init__(self, time):
        """
        QThread class.

        ---------
        Parameter:
        time: float
            Measurement time in sec.
        """

        self.bool = True
        self.time = time
        super().__init__()

    def loading(self):
        """"
        Update of the progressbar.
        """

        for i in range(1, self.time + 1):
            if self.bool == False:
                return
                
            sleep(1)
            self.change_value.emit(i)


class Measure_QT(QObject):
    finished = pyqtSignal()
    off = pyqtSignal()
    msg_error = pyqtSignal(str)

    def __init__(self, devices):
        """Initialization of the measurement QThread.

        Args:
            devices (dict): Contains all devices.
        """
        super().__init__()
        self.devices = devices

    def meas(self):
        PS_step = np.inf
        VNA_step = np.inf
        # Iteration on PS, only one if PS is not used.
        while PS_step > 0:
            PS_step = self.devices['PS'].meas()
            self.devices['GM'].meas()
            # Iteration on VNA if VNA and SM are used together.
            while VNA_step > 0:
                VNA_step = self.devices['VNA'].meas()
                self.devices['SM'].meas()
                
    
def Plot(SM, VNA, PS):
    if SM or (VNA and PS):
        fig = plt.figure()
            
