import os
import pyvisa as visa
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
from Plot_GUI import *



###############################################################################
# This program is working with Interface.py file as parent, and Plot_GUI.py and Save.py files as children for SoftMeasure.
# It contains useful code allowing to launch proper measurement.
###############################################################################



class Valid:
    def __init__(self, parent):
        """
        Class called when "okay" button is clicked.

        ---------
        Parameter:
        parent: class
        """

        self.parent = parent
        self.kill = False


    def widget(self):
        """
        Display of plot frame widgets.
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
        """
        Event method when the "okay" button is clicked.
        """
        
        self.path = self.save.pathEdit.text()
        
        self.save_params()
        if self.check_kill():
            return
        
        self.folder()
        if self.check_kill():
            return
        
        self.connection()
        if self.check_kill():
            return
        
        self.initialization()
        if self.check_kill():
            return
        
        self.meas_record()


    def save_params(self):
        """
        Save last filled QWidget parameters.
        """

        try:
            if self.parent.vna.box.isChecked():
                self.parent.vna.save_params()

            if self.parent.ps.box.isChecked():
                self.parent.ps.save_params()

            if self.parent.gm.box.isChecked():
                self.parent.gm.save_params()

            if self.parent.sm.box.isChecked():
                self.parent.sm.save_params()
        
        except:
            self.kill = True


    def folder(self):
        """
        Create folder, subfolders and txt files for futur measurements to the chosen file path and instrument(s).
        """

        # Creating parent folder.
        try:
            os.makedirs(self.path)

        except FileExistsError:
            pass

        except FileNotFoundError:
            self.kill = True
            QMessageBox.about(self.parent, 'Warning', 'The specified path cannot be found.')
            return


        if self.parent.vna.box.isChecked():
            # Creating S folder if it does not exist.
            self.s_path = os.path.join(self.path, 'S')
            try:
                os.makedirs(self.s_path)

            except FileExistsError:
                pass

            # Creating frequency file with values.
            f_values = np.linspace(float(self.parent.vna.f_start.text()), float(self.parent.vna.f_stop.text()), int(self.parent.vna.nb_step.text()))
            np.savetxt(os.path.join(self.path, 'f_values.txt'), f_values, header='Frequency [GHz]', comments='')
            

            self.sij = ('S11', 'S12', 'S21', 'S22')
            for s in self.sij:
                # Creating Sij folders if they do not exist.
                path = os.path.join(self.s_path, s)
                try:
                    os.makedirs(path)

                except FileExistsError:
                    pass

                # Creating sij files.
                with open(os.path.join(path, 'Magnitude.txt'), 'w') as f:
                    f.write(f'{s} Magnitude [dB]\n')

                with open(os.path.join(path, 'Phase.txt'), 'w') as f:
                    f.write(f'{s} Phase [rad]\n')

        
        if self.parent.ps.box.isChecked():
            # Creating current file.
            with open(os.path.join(self.path, 'I_values.txt'), 'w') as f:
                f.write('Current [A]\n')

        if self.parent.gm.box.isChecked():
            # Creating magnetic field file.
            with open(os.path.join(self.path, 'H_values.txt'), 'w') as f:
                f.write('Magnetic Field [' + self.parent.gm.unit.currentText() + ']\n')

        if self.parent.sm.box.isChecked():
            # Creating iSHE voltage file.
            with open(os.path.join(self.path, 'V-iSHE_values.txt'), 'w') as f:
                f.write('iSHE Voltage [V]\n')

            # Creating iSHE delta (error) iSHE voltage file.
            with open(os.path.join(self.path, 'Delta_V-iSHE_values.txt'), 'w') as f:
                f.write('Detla iSHE Voltage [V]\n')


    def connection(self):
        """
        Connection to the chosen instrument(s).
        """

        self.rm = visa.ResourceManager()
        
        if self.parent.ps.box.isChecked():
            try:
                self.parent.ps.connection(self.rm)
                if self.check_current_supplied():
                    # If the current supplied is higher than the max allowed value: return to the home window.
                    return
                
            except:
                return self.msg_error('PS')


        if self.parent.vna.box.isChecked():
            try:
                self.parent.vna.connection(self.rm)

            except:
                return self.msg_error('VNA')
        

        if self.parent.gm.box.isChecked():
            try:
                self.parent.gm.connection(self.rm)

            except:
                return self.msg_error('GM')


        if self.parent.sm.box.isChecked():
            try:
                self.parent.sm.connection(self.rm)
                
            except:
                return self.msg_error('SM')


    def initialization(self):
        """
        Initialization to the chosen instrument(s).
        """

        if self.parent.vna.box.isChecked():
            try:
                self.parent.vna.initialization()

            except:
                self.off()
                return self.msg_error('VNA')

        if self.parent.ps.box.isChecked():
            try:
                self.parent.ps.initialization()

            except:
                self.off()
                return self.msg_error('PS')

        if self.parent.gm.box.isChecked():
            try:
                self.parent.gm.initialization()

            except:
                self.off()
                return self.msg_error('GM')

        if self.parent.sm.box.isChecked():
            try:
                self.parent.sm.initialization()

            except:
                self.off()
                return self.msg_error('SM')
   

    def meas_record(self):
        """
        Launching measurement.
        """

        # Measurement class.
        self.meas = Measure_QT(self.parent, self.path, self.s_path)

        # Connecting signals of the measurement class.
        self.meas.msg_error.connect(self.msg_error)
        self.meas.off.connect(self.off)
        self.emergency.clicked.connect(self.meas.bool_switch)

        # Measurement in parralel (creation of a measurement Qhread).
        if self.parent.vna.box.isChecked() and self.parent.sm.box.isChecked():

            # Creating measurement QThread
            self.meas_thread = QThread()
            self.meas.moveToThread(self.meas_thread)

            self.meas_thread.started.connect(self.meas.meas)
            self.meas.finished.connect(self.meas_thread.exit)

            # Creating plot window
            self.plot_gui = Plot_GUI(self.parent)

            self.nb_step = int(float(self.parent.vna.nb_step.text()))
            self.plot_gui.S_QT(os.path.join(self.s_path, 'S21/Magnitude.txt'))
            self.plot_gui.V_QT(os.path.join(self.path, 'V-iSHE_values.txt'), os.path.join(self.path, 'Delta_V-iSHE_values.txt'))

            self.meas.plots.connect(self.plot_gui.S_curve)
            self.meas.plots.connect(self.plot_gui.V_curve)
            self.meas.Vwatcher.connect(self.plot_gui.Vwatcher.read_data.emit)
            self.meas.Swatcher.connect(self.plot_gui.Swatcher.read_data.emit)
            self.meas.finished.connect(self.meas_thread.exit)

            self.meas_thread.start()
        
        #Measurement in serie.
        else:
            self.parent.vna.meas_settings(self.parent.vna.nb_step.text(), self.parent.vna.f_start.text(), self.parent.vna.f_stop.text())
            self.meas.meas()

        self.launch_progressbar()


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

        self.pb_qt.bool = False
        self.display_time.setText('')
        self.progressbar.setValue(0)
        self.progressbar.setVisible(False)
        self.estimated_time.setVisible(False)
        self.display_time.setVisible(False)
        self.emergency.setVisible(False)


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
        """
        Turn off instrument(s).
        """
        
        try:
            self.meas.finished.emit()
        except:
            pass

        try:
            self.pb_qt.finished.emit()
        except:
            pass

        try:
            self.plot_gui.Vthread.exit()
            self.plot_gui.Sthread.exit()
        except:
            pass
        
        if self.parent.vna.box.isChecked():
            self.parent.vna.off()

        if self.parent.ps.box.isChecked():
            self.parent.ps.off()

        if self.parent.gm.box.isChecked():
            self.parent.gm.off()

        if self.parent.sm.box.isChecked():
            self.parent.sm.off()
        
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

    def __init__(self, parent, path, s_path):
        """
        QThread class.

        ---------
        Parameters:
        parent: class
        
        path: str

        s_path: str
        """

        super().__init__()
        self.parent = parent
        self.path = path
        self.s_path = s_path
        self.bool = True
        self.sij = ('S11', 'S12', 'S21', 'S22')


    def meas_step(self, idx):
        """
        One measurement step: measurement of VNA and SM.

        ---------
        Parameter:
        idx: int
            Index bound to the PS iteration, otherwise equal to 0.
        """

        # VNA Sweep of one frequency and the same + 1 Hz.
        if self.parent.vna.box.isChecked() and self.parent.sm.box.isChecked():
            for i, freq in enumerate(self.freq_list):
                if self.bool == False:
                    return

                self.parent.vna.meas_settings('2', str(freq), str(freq + 1e-9))
                self.parent.vna.read_s_param()

                sm_list = []
                start = now = time()

                # Set of SM measurement while a given time.
                while now - start < self.sm_time:
                    self.parent.sm.read_val()
                    sm_list.append(self.parent.sm.instr.V)
                    now = time()
                
                # Recording in files SM measurements.
                self.sm_record(i, self.len_freq_list, idx, np.array(sm_list))
                    
                # Recording in files VNA measurements.
                self.vna_record(i, self.len_freq_list, idx)

        # Set of SM measurement while a given time.
        elif self.parent.sm.box.isChecked():
            
            while now - start < self.sm_time:
                self.parent.sm.read_val()
                sm_list.append(self.parent.sm.instr.V)
                now = time()
                    
            # Recording in files SM measurements.
            self.sm_record(idx, 0, idx, np.array(sm_list))

        # VNA Sweep.
        elif self.parent.vna.box.isChecked():
            self.parent.vna.meas_settings(self.parent.vna.nb_step.text(), self.parent.vna.f_start.text(), self.parent.vna.f_stop.text())
            self.parent.vna.read_s_param()

            # Recording in files VNA measurements.
            self.vna_record(idx, 0, idx)
        print('finished')

                
    def meas(self):
        """
        Main measurement method.
        """
        
        # Creation of the VNA frequency sweep list.
        if self.parent.vna.box.isChecked():
            self.freq_list = np.linspace(float(self.parent.vna.f_start.text()), float(self.parent.vna.f_stop.text()), int(self.parent.vna.nb_step.text()))
            self.len_freq_list = len(self.freq_list)

        if self.parent.sm.box.isChecked():
            self.sm_time = float(self.parent.sm.meas_time.text())

        if self.parent.ps.box.isChecked():
            # Creation of the PS current sweep list.
            self.amp_list = np.linspace(float(self.parent.ps.I_start.text()), float(self.parent.ps.I_stop.text()), int(self.parent.ps.nb_step.text()))
            self.len_amp_list = len(self.amp_list)

            # Set of colors
            normalize = mcolors.Normalize(vmin=0, vmax=len(self.amp_list))
            colormap = cm.jet
            self.colors = [colormap(normalize(n)) for n in range(len(self.amp_list))]

            for i, amp in enumerate(self.amp_list):
                if self.bool == False:
                    print('COUCOU')
                    return self.off.emit()

                # Creation of a new curve for each plots.
                self.plots.emit(self.colors[i])
                self.parent.ps.set_current(amp)

                # Recording of the current value.
                with open(os.path.join(self.path, 'I_values.txt'), 'a') as f:
                    f.write(str(amp) + '\n')

                # Launching if a measurement step (VNA + SM).
                self.meas_step(i)

                # Measurement of the static magnetic field.
                if self.parent.gm.box.isChecked():
                    self.parent.gm.read_mag_field()

                    # Recording of the static magnetic field value.
                    with open(os.path.join(self.path, 'H_values.txt'), 'a') as f:
                        f.write(self.parent.gm.instr.mag_value + '\n')
                # New row for the next measurement step for the VNA and SM files.
                sij = ['S11', 'S12', 'S21', 'S22']
                for s in sij:
                    path = os.path.join(self.s_path, s)
                    with open(os.path.join(path, 'Magnitude.txt'), 'a') as f:
                        f.write('\n')
                            
                    with open(os.path.join(path, 'Phase.txt'), 'a') as f:
                        f.write('\n')

                with open(os.path.join(self.path, 'V-iSHE_values.txt'), 'a') as f:
                    f.write('\n')

                with open(os.path.join(self.path, 'Delta_V-iSHE_values.txt'), 'a') as f:
                    f.write('\n')


        else:
            self.len_amp_list = 0
            self.plots.emit((0, 0, 1, 1))
            self.meas_step(0)
        
        self.off.emit()

    
    def sm_record(self, idx, len_loop, idx_amp, meas):
        """
        Recording SM measurement if a thread measurement is used.

        ---------
        Parameters:
        idx: int
            Index bound to the PS iteration, otherwise equal to 0.

        len: int
            len of the loop.
        
        idx_amp: int
            index of the current applied current.

        meas: array
            Set of measurement to making an average.
        """

        # Averaging.
        mean_meas = mean(meas)

        # Delta (error).
        sigma = max(abs(meas - mean_meas))

        # Recording of the averaging value.
        with open(os.path.join(self.path, 'V-iSHE_values.txt'), 'a') as f:
            f.write(str(mean_meas))
            if self.parent.vna.box.isChecked() and idx < len_loop-1:
                f.write(', ')
                    

        # Recording of the delta value.
        with open(os.path.join(self.path, 'Delta_V-iSHE_values.txt'), 'a') as f:
            f.write(str(sigma))
            if self.parent.vna.box.isChecked() and idx < len_loop-1:
                f.write(', ')

        # Reading of the file for the plotting.
        try:
            self.Vwatcher.emit(idx_amp)
        
        except:
            pass


    def vna_record(self, idx, len_loop, idx_amp):
        """
        Recording S-parameters of the VNA measurement if a thread measurement is used.

        ---------
        Parameter:
        idx: int
            Index bound to the PS iteration, otherwise equal to 0.

        len: int
            len of the loop.
        
        idx_amp: int
            index of the current applied current.
        """
        
        for s in self.sij:
            path = os.path.join(self.s_path, s)
            # Recording of the magnitude value.
            with open(os.path.join(path, 'Magnitude.txt'), 'a') as f:
                s_list = getattr(self.parent.vna.instr, s)['mag']
                if self.parent.sm.box.isChecked():
                    f.write(str(s_list[0]))
                    if idx < len_loop-1:
                        f.write(', ')
                
                else:
                    s_len = len(s_list)
                    for i, val in enumerate(s_list):
                        f.write(str(val))
                        if i < s_len-1:
                            f.write(', ')
            
            # Recording of the phase value.
            with open(os.path.join(path, 'Phase.txt'), 'a') as f:
                s_list = getattr(self.parent.vna.instr, s)['mag']
                if self.parent.sm.box.isChecked():
                    f.write(str(s_list[0]))
                    if idx < len_loop-1:
                        f.write(', ')
                
                else:
                    s_len = len(s_list)
                    for i, val in enumerate(s_list):
                        f.write(str(val))
                        if i < s_len-1:
                            f.write(', ')

        # Reading of the file for the plotting.
        try:
            self.Swatcher.emit(idx_amp)

        except:
            pass

    
    def bool_switch(self):
        """
        Stop measurement if the emergency button has been clicked.
        """
        
        self.bool = False
