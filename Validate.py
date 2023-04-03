import os
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
        self.devices['sm'](VNA_step)
        
        for key, value, in self.devices.items():
            if key != 'sm' or key != 'vna':
                value.connection()

    def initialization(self):
        """Initialization to the chosen instrument(s).
        """
        for value in self.devices.values():
            value.initialization()

    def meas_record(self):
        """
        Launching measurement.
        """

        """# Measurement class.
        self.meas = Measure_QT(self.parent, self.path, self.s_path)

        # Connecting signals of the measurement class.
        self.meas.msg_error.connect(self.msg_error)
        self.meas.off.connect(self.off)
        self.emergency.clicked.connect(self.meas.bool_switch)

        # Creating measurement QThread
        self.meas_thread = QThread()
        self.meas.moveToThread(self.meas_thread)

        self.meas_thread.started.connect(self.meas.meas)
        self.meas.finished.connect(self.meas_thread.exit)

        # Creating plot window
        if self.parent.vna.box.isChecked() and self.parent.sm.box.isChecked():
            self.plot_gui = Plot_GUI(self.parent)

            self.nb_step = int(float(self.parent.vna.nb_step.text()))
            self.plot_gui.S_QT(os.path.join(self.s_path, 'S21/Magnitude.txt'))
            self.plot_gui.V_QT(os.path.join(self.path, 'V-iSHE_values.txt'), os.path.join(self.path, 'Delta_V-iSHE_values.txt'))

            self.meas.plots.connect(self.plot_gui.S_curve)
            self.meas.plots.connect(self.plot_gui.V_curve)
            self.meas.Vwatcher.connect(self.plot_gui.Vwatcher.read_data.emit)
            self.meas.Swatcher.connect(self.plot_gui.Swatcher.read_data.emit)
            self.meas.finished.connect(self.meas_thread.exit)

        elif self.parent.vna.box.isChecked():
            self.parent.vna.meas_settings(self.parent.vna.nb_step.text(), self.parent.vna.f_start.text(), self.parent.vna.f_stop.text())

        self.meas_thread.start()
        self.launch_progressbar()"""
        
        
        if self.parent.vna.box.isChecked():
            self.freq_list = np.linspace(float(self.parent.vna.f_start.text()), float(self.parent.vna.f_stop.text()), int(self.parent.vna.nb_step.text()))
            self.len_freq_list = len(self.freq_list)
            
        if self.parent.sm.box.isChecked():
            self.sm_time = float(self.parent.sm.meas_time.text())
            
        if self.parent.ps.box.isChecked():
            # Creation of the PS current sweep list.
            self.amp_list = np.linspace(float(self.parent.ps.I_start.text()), float(self.parent.ps.I_stop.text()), int(self.parent.ps.nb_step.text()))
            self.len_amp_list = len(self.amp_list)
            
            for i, amp in enumerate(self.amp_list):
                    if self.bool == False:
                        return self.off()
                    
     
    


    def msg_error(self, device):
        """
        Display of a message error due to the displayed device.

        ---------
        Parameter:
        device: str
            Device malfunctionning
        """

        if device == 'VNA':
            word = 'VNA'

        elif device == 'PS':
            word = 'Power Supply'

        elif device == 'GM':
            word = 'GaussMeter'

        elif device == 'SM':
            word = 'SourceMeter'

        self.kill = True
        QMessageBox.about(self.parent, 'Error', f'Connection issue with {word}.')


    def launch_progressbar(self):
        """
        Display of the progressbar.
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


    def check_current_supplied(self):
        """
        Checking the current supplied. If it is higher than the threshold, the current will not be applied. If it is higher than 16 A: Ask if the user want to continue.
        """

        if self.parent.ps.box.isChecked() and (abs(float(self.parent.ps.I_start.text())) > self.parent.ps.instr.I_max or abs(float(self.parent.ps.I_stop.text())) > self.parent.ps.instr.I_max):
            QMessageBox.about(self.parent, 'Warning', 'The current limit of the Power Supply is 38 A.')
            self.kill = True
            return self.kill

        elif self.parent.ps.box.isChecked() and (abs(float(self.parent.ps.I_start.text())) >= 16 or abs(float(self.parent.ps.I_stop.text())) >= 16):
            msgbox = QMessageBox()
            msgbox.setWindowTitle('Warning')
            msgbox.setText('The applied current of the Power Supply is high, do you want to continue?')
            msgbox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

            return_value = msgbox.exec()
            if return_value == QMessageBox.No:
                self.kill = True
                return self.kill
        
        QMessageBox.about(self.parent, 'Warning', 'Do not forget to start the cooling circuit.')


    def check_kill(self):
        """
        Checking if an issue has occured.
        """

        if self.kill:
            self.kill = False
            self.off()
            return True
        
        else:
            return False


    def off(self):
        """Turn off chosen instrument(s).
        """
        for value in self.devices.values():
            value.off()
        #Voir quoi faire de ça
        self.okay.setEnabled(True)



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
    plots = pyqtSignal(tuple)
    Vwatcher = pyqtSignal(int)
    Swatcher = pyqtSignal(int)

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
        while PS_step > 0:
            # It is necessary to 
            PS_step = self.devices['PS'].meas()
            while VNA_step > 0:
                VNA_step = self.devices['VNA'].meas()
                for key, value, in self.devices.items():
                    if key != 'PS' or key != 'VNA':
                        value.meas()
            
