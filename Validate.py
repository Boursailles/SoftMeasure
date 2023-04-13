import os
import sys
import traceback
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.colors as mcolors
import matplotlib.cm as cm
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from time import sleep, time
from statistics import mean
import numpy as np
import math
from Save import *


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
        self.widget()

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
        self.emergency.setStyleSheet(
            "*{border-image: url(Emergency_button.png);} :hover{ border-image: url(Emergency_button_hovered.png);}")
        self.emergency.setFixedWidth(40)
        self.emergency.setFixedHeight(40)
        self.emergency.setVisible(False)
        retainsize = self.emergency.sizePolicy()
        retainsize.setRetainSizeWhenHidden(True)
        self.emergency.setSizePolicy(retainsize)
        self.emergency.clicked.connect(self.emergency_stop)

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
        print('wow')
        self.path = self.save.pathEdit.text()

        self.save_params()
        self.folder()
        self.connection()
        self.initialization()
        self.measurement()

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
            os.makedirs(self.path)
        except FileExistsError:
            pass
        # reating subfiles and/or subfolders.
        for value in self.devices.values():
            value.file(self.path)

    def connection(self):
        """Connection to the chosen instrument(s).
        """
        sm_connected = self.devices['sm'].box.isChecked()
        # Measurement method for the VNA device depends if the SM one is used or not.
        VNA_step = self.devices['vna'].connection(sm_connected)
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
        
        # Creating measurement QThread.
        self.meas_thread = QThread()
        self.meas.moveToThread(self.meas_thread)
        self.meas_thread.started.connect(self.meas.meas)
        self.meas.off.connect(self.meas_thread.exit)
        self.meas.finished.connect(self.off)
        self.meas.signal_exception.connect(self.error_handler)
        
        # Plot GUI and signals for plots.
        """self.measurement_plot = Plot(self.devices) # Plot window creation.
        self.meas.create_traces.connect(self.measurement_plot.create_traces)
        self.meas.update_traces.connect(self.measurement_plot.update_traces)
        self.meas.update_surfaces.connect(self.measurement_plot.update_surfaces)"""

        # Launch measurement and progressbar.
        self.meas_thread.start()
        '''self.launch_progressbar()'''
        self.emergency.setVisible(True)

    def error_handler(self, type, value, traceback_obj):
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
        tcb = ''.join(traceback.format_tb(traceback_obj)).replace('\n', '<br>')
        msg.setInformativeText(
            f'<span style="color: red;"><b>{type.__name__}:<b></span> {value}<br><br><span style="color: black;"><b>Traceback:<b></span><br>{tcb}')
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

        """tcb = ''.join(traceback.format_tb(traceback_obj))
        print(f'{type.__name__}\n{type.__name__}\n{tcb}')
        tcb = ''.join(traceback.format_tb(traceback_obj))
        
        self.off()"""

    def off(self):
        """Turn off instrument(s).
        """
        try:
            self.emergency_stop()
            self.meas.off.emit()
        except AttributeError:
            pass
        for value in self.devices.values():
            value.off()
        self.okay.setEnabled(True)
        self.emergency.setVisible(False)

    def emergency_stop(self):
        """Stop measurement.
        """
        self.meas.emergency_clicked = True


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
    """QThread for measurement.

    Args:
        QObject (object): Object from PyQT5.
    """
    # Functionnalities signals.
    signal_exception = pyqtSignal(object, object, object) # If an exception occur, it'll be sent and managed by the main thread.
    finished = pyqtSignal() # Warns when measurement is finished.
    off = pyqtSignal() # Break the current thread.
    # Plot signals.
    create_traces = pyqtSignal()
    update_traces = pyqtSignal(float)
    update_surfaces = pyqtSignal()

    def __init__(self, devices):
        """Initialization of the measurement QThread.

        Args:
            devices (dict): Contains all devices.
        """
        super().__init__()
        self.devices = devices
        self.emergency_clicked = False # Initialization of the emergency button. If True: stop the measurement. Default to False.

    def meas(self):
        """Measurement management.
        """
        try:
            # Initialize step number for PS device.
            PS_step = np.inf
            
            
            # Iteration on PS, only one if PS is not used.
            while PS_step > 0:
                # Initialize step number VNA device.
                VNA_step = np.inf
                self.devices['vna'].initialize_steps()
                self.devices['sm'].initialize_steps()
                
                self.create_traces.emit() # Creation of trace plots.
                PS_step = self.devices['ps'].meas()
                self.devices['gm'].meas()
                # Iteration on VNA if VNA and SM are used together.
                while VNA_step > 0:
                    VNA_step = self.devices['vna'].meas()
                    V = self.devices['sm'].meas()
                    self.update_traces.emit(V) # Updates traces plots.
                    # For each iteration, check if the emergency button was clicked, if yes, the measurement is stopped.
                    if self.emergency_clicked:
                        self.finished.emit()
                        break
                self.update_surfaces.emit() # Updates surfaces plots.
            self.finished.emit()
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.signal_exception.emit(exc_type, exc_value, exc_traceback)


class Plot(QWidget):
    def __init__(self, devices):
        super().__init__()
        self.setWindowTitle('SoftMeasure')
        self.devices = devices
        SM = devices['sm'].box.isChecked()
        VNA = devices['vna'].box.isChecked()
        PS = devices['ps'].box.isChecked()
        # Default functions for traces and surfaces.

        def CT():
            pass
        self.create_traces = CT

        def UT(SM_value):
            pass
        self.update_traces = UT

        def US():
            pass
        self.update_surfaces = US

        if (SM and VNA) or (SM and PS) or (VNA and PS):
            self.create_subplots(SM, VNA, PS)
            # Créer l'application et la fenêtre
            layout = QVBoxLayout()
            self.setLayout(layout)
            # Ajouter le graphique dans la fenêtre
            canvas = FigureCanvas(self.fig)
            layout.addWidget(canvas)
            # Afficher la fenêtre
            self.show()

    def create_subplots(self, SM, VNA, PS):
        # 2D and surface plots for SM and VNA.
        if SM and VNA and PS:
            self.create_SM_VNA_PS_plot()
        # 2D plots for SM and VNA.
        elif SM and VNA:
            self.create_SM_VNA_plot()
        # Surface plot for SM.
        elif SM and PS:
            self.create_SM_PS_plot()
        # Surface plot for VNA.
        elif VNA and PS:
            self.create_VNA_PS_plot()

    # Methods to create plots.
    def create_SM_VNA_PS_plot(self):
        self.fig, ax = plt.subplots(2, 2, constrained_layout=True)
        self.I = np.linspace(float(self.devices['ps'].settings['I_start']), float(
            self.devices['ps'].settings['I_stop']), int(self.devices['ps'].settings['nb_step']))
        self.f = np.linspace(float(self.devices['vna'].settings['f_start']), float(
            self.devices['vna'].settings['f_stop']), int(self.devices['vna'].settings['nb_step']))

        # Initializing surfaces.
        self.SM_surface_data = np.array([])
        self.VNA_surface_data = np.array([])

        # Initialization VNA trace subplot.
        ax[0, 0].set_xlim(min(self.f), max(self.f))
        ax[0, 0].set_ylabel('$S_{21}$ [dB]')
        ax[0, 0].set_xticklabels([])
        self.VNA_trace, = ax[0, 0].plot([], [])

        # Initialization SM trace subplot.
        ax[1, 0].set_xlim(min(self.f), max(self.f))
        ax[1, 0].set_xlabel('Frequency [GHz]')
        ax[1, 0].set_ylabel('$V_{iSHE}$ [V]')
        self.SM_trace, = ax[1, 0].plot([], [])

        # Initialization VNA surface subplot.
        ax[0, 1].set_xlim(min(self.I), max(self.I))
        ax[0, 1].set_ylim(min(self.f), max(self.f))
        ax[0, 1].set_ylabel('Frequency [GHz]')
        ax[0, 1].set_xticklabels([])
        self.VNA_surface = ax[0, 1].plot_surface([], [], [])

        # Initialization SM surface subplot.
        ax[1, 1].set_xlim(min(self.I), max(self.I))
        ax[1, 1].set_ylim(min(self.f), max(self.f))
        ax[1, 1].set_xlabel('Current [A]')
        ax[1, 1].set_ylabel('Frequency [GHz]')
        self.SM_surface = ax[0, 1].plot_surface([], [], [])

        def CT():
            self.create_SM_trace()
            self.create_VNA_trace()
        self.create_traces = CT

        def UT(SM_value):
            self.update_SM_trace(SM_value)
            self.update_VNA_trace(
                self.devices['vna'].instr.S21['Magnitude'][0])
        self.update_traces = UT

        def US():
            self.update_SM_surface(self.SM_surface_data)
            self.update_VNA_surface(self.VNA_trace_data)
        self.update_surfaces = US

    def create_SM_VNA_plot(self):
        self.fig, ax = plt.subplots(2, 1, constrained_layout=True)
        self.f = np.linspace(float(self.devices['vna'].settings['f_start']), float(
            self.devices['vna'].settings['f_stop']), int(self.devices['vna'].settings['nb_step']))

        # Initialization VNA trace subplot.
        ax[0].set_xlim(min(self.f), max(self.f))
        ax[0].set_ylabel('$S_{21}$ [dB]')
        ax[0].set_xticklabels([])
        self.VNA_trace, = ax[0].plot([], [])

        # Initialization SM trace subplot.
        ax[1].set_xlim(min(self.f), max(self.f))
        ax[1].set_xlabel('Frequency [GHz]')
        ax[1].set_ylabel('$V_{iSHE}$ [V]')
        self.SM_trace, = ax[1].plot([], [])

        def CT():
            self.create_SM_trace()
            self.create_VNA_trace()
        self.create_traces = CT

        def UT(SM_value):
            self.update_SM_trace(SM_value)
            self.update_VNA_trace(
                self.devices['vna'].instr.S21['Magnitude'][0])
        self.update_traces = UT

    def create_SM_PS_plot(self):
        self.fig, ax = plt.subplots(constrained_layout=True)
        self.I = np.linspace(float(self.devices['PS'].settings['I_start']), float(
            self.devices['PS'].settings['I_stop']), int(self.devices['PS'].settings['nb_step']))

        # Initializing trace.
        self.SM_trace_data = np.array([])

        # Initialization SM trace subplot.
        ax.set_xlim(min(self.f), max(self.f))
        ax.set_xlabel('Frequency [GHz]')
        ax.set_ylabel('$V_{iSHE}$ [V]')
        self.SM_trace, = ax.plot([], [])

        def UT(SM_value):
            self.update_SM_trace(SM_value)
        self.update_traces = UT

    def create_VNA_PS_plot(self):
        self.fig, ax = plt.subplots(constrained_layout=True)
        self.I = np.linspace(float(self.devices['ps'].settings['I_start']), float(
            self.devices['ps'].settings['I_stop']), int(self.devices['ps'].settings['nb_step']))
        self.f = np.linspace(float(self.devices['vna'].settings['f_start']), float(
            self.devices['vna'].settings['f_stop']), int(self.devices['vna'].settings['nb_step']))

        # Initializing surface.
        self.VNA_surface_data = np.array([])

        # Initialization VNA surface subplot.
        ax.set_xlim(min(self.I), max(self.I))
        ax.set_ylim(min(self.f), max(self.f))
        ax.set_ylabel('Frequency [GHz]')
        ax.set_xticklabels([])
        self.VNA_surface = ax.plot_surface([], [], [])
        """ax[0, 1].colorbar(cmap='viridis')"""

        def US():
            self.update_VNA_surface(self.VNA_trace_data)
        self.update_surfaces = US

    # Methods to create traces.
    def create_SM_trace(self):
        self.SM_trace_data = np.array([])

    def create_VNA_trace(self):
        self.VNA_trace_data = np.array([])

    # Methods to update traces and surfaces.
    def update_SM_trace(self, SM_value):
        np.append(self.SM_trace_data, SM_value)
        self.SM_trace.set_data(self.f(len(self.SM_trace_data)), self.SM_trace_data)
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def update_SM_surface(self, SM_trace):
        np.append(self.SM_surface_data, SM_trace)
        I, f = np.meshgrid(self.I[len(self.SM_surface_data)], self.f)
        self.SM_surface.set_data(I, f, self.SM_surface_data)
        self.SM_surface.changed()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def update_VNA_trace(self, VNA_value):
        np.append(self.VNA_trace_data, VNA_value)
        self.VNA_trace.set_data(self.f(len(self.VNA_trace_data)), self.VNA_trace_data)
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def update_VNA_surface(self, VNA_trace):
        np.append(self.VNA_surface_data, VNA_trace)
        I, f = np.meshgrid(self.I[len(self.VNA_surface_data)], self.f)
        self.VNA_surface.set_data(I, f, self.VNA_surface_data)
        self.VNA_surface.changed()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
