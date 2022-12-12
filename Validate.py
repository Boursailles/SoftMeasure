import os
import pyvisa as visa
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QObject, QThread, pyqtSignal, Qt
from time import sleep, time
from statistics import mean 
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.cm as cm
from Save import *
from Interface import *
from Plot_GUI import *



###############################################################################
# This program is working with Interface.py file for SoftMeasure.
# It contains useful code allowing to launch proper measurement.
###############################################################################



class Valid:
    def __init__(self, parent):
        self.parent = parent

        self.kill = False


    def widget(self):
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


        layout = QGridLayout()

        layout.addWidget(self.save.box, 0, 0)
        layout.addWidget(self.okay, 0, 1)
        layout.addWidget(self.cancel, 0, 2)
        layout.addWidget(self.progressbar, 1, 0)
        layout.addWidget(self.estimated_time, 1, 1)
        layout.addWidget(self.display_time, 1, 2)

        self.box.setLayout(layout)


    def okay_event(self):
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
            # Creating S and Sij folders if they did not exist.
            self.s_path = os.path.join(self.path, 'S')
            try:
                os.makedirs(self.s_path)
            except FileExistsError:
                pass
            # Creating sij files.
            f_values = np.linspace(float(self.parent.vna.f_start.text()), float(self.parent.vna.f_stop.text()), int(self.parent.vna.nb_step.text()))
            np.savetxt(os.path.join(self.path, 'f_values.txt'), f_values, header='Frequency [GHz]', comments='')
                
            self.sij = ('S11', 'S12', 'S21', 'S22')
            for s in self.sij:
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

            with open(os.path.join(self.path, 'Delta_V-iSHE_values.txt'), 'w') as f:
                f.write('Detla iSHE Voltage [V]\n')


    def connection(self):
        self.rm = visa.ResourceManager()
        
        if self.parent.ps.box.isChecked():
            try:
                self.parent.ps.connection(self.rm)
                if self.check_current_supplied():
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
        if self.parent.vna.box.isChecked():
            try:
                self.parent.vna.initialization()
            except:
                return self.msg_error('VNA')

        if self.parent.ps.box.isChecked():
            try:
                self.parent.ps.initialization()
            except:
                return self.msg_error('PS')

        if self.parent.gm.box.isChecked():
            try:
                self.parent.gm.initialization()
            except:
                # If vna and/or ps are connected, then put them off.
                self.off()
                return self.msg_error('GM')

        if self.parent.sm.box.isChecked():
            try:
                self.parent.sm.initialization()
            except:
                return self.msg_error('SM')
   

    def meas_record(self):
        if self.vna.box.isChecked() and self.sm.box.isChecked():
            # Creating measurement QThread
            self.meas_thread = QThread()
            self.meas_qt = Measure_QT(self.parent, self.path, self.s_path)

            self.meas_qt.moveToThread(self.meas_thread)

            self.meas_qt.end_progressbar.connect(self.end_progressbar)
            self.meas_qt.off.connect(self.off)
            self.meas_qt.msg_error.connect(self.msg_error)
            self.meas_qt.meas_vna.connect(self.vna_record)
            self.meas_qt.meas_sm.connect(self.sm_record)

            self.meas_thread.started.connect(self.meas_qt.meas_record)

            self.meas_qt.finished.connect(self.meas_thread.quit)
            self.meas_qt.finished.connect(self.meas_qt.deleteLater)
            self.meas_thread.finished.connect(self.meas_qt.deleteLater)


            # Create Plotting window
            self.plot_gui = Plot_GUI(self.parent)

            self.nb_step = int(float(self.parent.vna.nb_step.text()))
            self.plot_gui.S_QT(os.path.join(self.s_path, 'S21/Magnitude.txt'))
            self.plot_gui.V_QT(os.path.join(self.path, 'V-iSHE_values.txt'))

            self.meas_qt.plots.connect(self.plot_gui.S_curve)
            self.meas_qt.plots.connect(self.plot_gui.V_curve)

            self.launch_progressbar()
            self.meas_thread.start()


    def sm_record(self, idx, meas):
        mean_meas = mean(meas)
        sigma = max(abs(meas - mean_meas))
        with open(os.path.join(self.path, 'V-iSHE_values.txt'), 'a') as f:
                            f.write(mean_meas + ', ')

        with open(os.path.join(self.path, 'Delta_V-iSHE_values.txt'), 'a') as f:
                f.write(sigma + ', ')

        self.plot_gui.Vwatcher.read_data.emit(idx)


    def vna_record(self, idx):
        # Recording of S-parameters
        for s in self.sij:
            path = os.path.join(self.s_path, s)
            with open(os.path.join(path, 'Magnitude.txt'), 'a') as f:
                for val in getattr(self.parent.vna.instr, s)['mag']:
                    f.write(f'{val[0]}, ')
                       
            with open(os.path.join(path, 'Phase.txt'), 'a') as f:
                for val in getattr(self.parent.vna.instr, s)['phase']:
                    f.write(f'{val[0]}, ')

        # Plot of S curve
        self.plot_gui.Swatcher.read_data.emit(idx)


    def msg_error(self, device):
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
        self.okay.setDisabled(True)
        self.time = None
        time_vna = 0
        time_sm = 0

        if self.parent.vna.box.isChecked():
            time_vna = int(float(self.parent.vna.sw_time.text()))

        if self.parent.sm.box.isChecked():
            time_sm = int(float(self.parent.sm.meas_time.text()))

            if self.parent.vna.box.isChecked():
                time_sm *= int(self.parent.vna.nb_step.text())


        self.time = max(time_vna, time_sm)

        if self.parent.ps.box.isChecked():
            self.time *= int(self.parent.ps.nb_step.text())


        if self.time != None:
            self.progressbar.setMinimum(0)
            self.progressbar.setMaximum(self.time)
            self.set_progressbar_val(0)
            self.progressbar.setVisible(True)
            self.estimated_time.setVisible(True)
            self.display_time.setVisible(True)

            self.pb_thread = QThread()
            self.pb_qt = Progressbar_QT(self.time)

            self.pb_qt.moveToThread(self.pb_thread)
            self.pb_thread.started.connect(self.pb_qt.loading)

            self.pb_qt.change_value.connect(self.set_progressbar_val)

            self.pb_qt.finished.connect(self.pb_thread.quit)
            self.pb_qt.finished.connect(self.pb_qt.deleteLater)
            self.pb_qt.finished.connect(self.end_progressbar)
            self.pb_thread.finished.connect(self.pb_thread.deleteLater)

            self.pb_thread.start()


    def set_progressbar_val(self, val):
        self.progressbar.setValue(val)

        hour = str((self.time - val)//3600)
        if len(hour) == 1:
            hour = '0' + hour
        min = str((self.time - val)%3600//60)
        if len(min) == 1:
            min = '0' + min
        sec = str((self.time - val)%3600%60)
        if len(sec) == 1:
            sec = '0' + sec
        self.display_time.setText(hour + ':' + min + ':' + sec)


    def end_progressbar(self):
        self.okay.setEnabled(True)
        self.progressbar.setVisible(False)
        self.estimated_time.setVisible(False)
        self.display_time.setVisible(False)


    def check_current_supplied(self):
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
        if self.kill:
            self.kill = False
            self.off()
            return True
        
        else:
            return False


    def off(self):
        if self.parent.vna.box.isChecked():
            self.parent.vna.off()

        if self.parent.ps.box.isChecked():
            self.parent.ps.off()

        if self.parent.gm.box.isChecked():
            self.parent.gm.off()

        if self.parent.sm.box.isChecked():
            self.parent.sm.off()



class Progressbar_QT(QObject):
    change_value = pyqtSignal(int)
    finished = pyqtSignal()
    def __init__(self, time):
        self.time = time
        super().__init__()


    def loading(self):
        for i in range(1, self.time + 1):
            sleep(1)
            self.change_value.emit(i)

        self.finished.emit()


class Measure_QT(QObject):
    finished = pyqtSignal()
    end_progressbar = pyqtSignal()
    off = pyqtSignal()
    msg_error = pyqtSignal(str)
    meas_sm = pyqtSignal(int, list)
    meas_vna = pyqtSignal(int)
    plots = pyqtSignal()

    def __init__(self, parent, path, s_path):
        super().__init__()
        self.parent = parent
        self.path = path
        self.s_path = s_path
        self.bool = True


    def meas_step(self, idx):
        for freq in self.freq_list:
            self.parent.vna.meas_settings(2, str(freq), str(freq + 1e-9))
            self.parent.vna.read_s_param()

            sm_list = []
            start = now = time()

            while now - start < 1:
                self.parent.sm.read_val()
                sm_list.append(self.parent.sm.instr.V)
                now = time()
            
            self.meas_vna.emit(idx)
            self.meas_sm.emit(idx, np.array(sm_list))


    def meas(self):
        self.freq_list = np.linspace(float(self.parent.vna.f_start.text()), float(self.parent.vna.f_stop.text()), int(self.parent.vna.nb_step.text()))

        if self.parent.ps.box.isChecked():
            self.amp_list = np.linspace(float(self.parent.ps.I_start.text()), float(self.parent.ps.I_stop.text()), int(self.parent.ps.nb_step.text()))

            # Set of colors
            normalize = mcolors.Normalize(vmin=0, vmax=len(self.amp_list))
            colormap = cm.jet
            self.colors = [colormap(normalize(n)) for n in range(len(self.amp_list))]

            for i, amp in enumerate(self.amp_list):
                self.plots.emit(self.colors[i])
                self.parent.ps.set_current(amp)
                with open(os.path.join(self.path, 'I_values.txt'), 'a') as f:
                    f.write(str(amp) + '\n')

                self.meas_step(i)

                if self.parent.gm.box.isChecked():
                    self.parent.gm.read_mag_field()

                    with open(os.path.join(self.path, 'H_values.txt'), 'a') as f:
                        f.write(self.parent.gm.instr.mag_value + '\n')

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
            self.plots.emit((1, 0, 0, 1))
            self.meas_step(0)