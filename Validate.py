import os
import pyvisa as visa
from PyQt5.QtCore import *
import numpy as np
from Save import *
from QThreads import *
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QObject, QThread, pyqtSignal, Qt
from Interface import *



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

        self.estimated_time = QLabel('Estimated time:')
        self.estimated_time.setVisible(False)

        self.display_time = QLabel('')
        self.display_time.setVisible(False)

        layout = QGridLayout()

        layout.addWidget(self.save.box, 0, 0)
        layout.addWidget(self.okay, 0, 1)
        layout.addWidget(self.cancel, 0, 2)
        layout.addWidget(self.progressbar, 1, 0)
        layout.addWidget(self.estimated_time, 1, 1)
        layout.addWidget(self.display_time, 1, 2)

        self.box.setLayout(layout)


    def okay_event(self):

        self.launch_progressbar()
    

        self.path = self.save.pathEdit.text()
        self.folder()
        if self.kill:
            self.kill = False
            return

        self.connection()
        if self.kill:
            self.kill = False
            return
        
        self.initialization()
        if self.kill:
            self.kill = False
            return
        
        self.meas_record()


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
                
            self.sij = ('S11', 'S12', 'S21', 'S22')
            for s in self.sij:
                path = os.path.join(self.s_path, s)
                try:
                    os.makedirs(path)
                except FileExistsError:
                    pass

                # Creating sij files.
                with open(os.path.join(path, 'Magnitude.txt'), 'w') as f:
                    f.write(f'{s} magnitude [dB]\n')

                with open(os.path.join(path, 'Phase.txt'), 'w') as f:
                    f.write(f'{s} phase [rad]\n')
        
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


    def connection(self):
        self.rm = visa.ResourceManager()

        if self.parent.vna.box.isChecked():
            try:
                self.parent.vna.connection(self.rm)
            except:
                return self.msg_error('VNA')

        if self.parent.ps.box.isChecked():
            try:
                self.parent.ps.connection(self.rm)
            except:
                return self.msg_error('PS')

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

        # Possibility to have last_status?
        '''if self.ps.box.isChecked():
            try:
                self.ps.connection(self.rm)

            except visa.VisaIOError as e:
                QMessageBox.about(self, "Warning", "Connection issue with electromagnet\nError Codes: " + self.rm.last_status+"\t" + self.rm.visalib.last_status)

        if self.gm.box.isChecked():
            try:
                self.gm.connection(self.rm)

            except visa.VisaIOError as e:
                QMessageBox.about(self, "Warning", "Connection issue with gaussmeter\nError Codes: " + self.rm.last_status+"\t" + self.rm.visalib.last_status)'''


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
        if self.parent.ps.box.isChecked():
            amps_list = np.linspace(self.parent.ps.I_start, self.parent.ps.I_stop, self.parent.ps.nb_step)

            for i, amps in enumerate(amps_list):
                try:
                    self.parent.ps.set_current(amps)
                    with open(os.path.join(self.path, 'I_values.txt'), 'a') as f:
                            f.write(str(amps) + '\n')
                
                except:
                    self.parent.ps.connection()
                    self.parent.ps.off()
                    try:
                        self.parent.vna.off()
                    except:
                        self.parent.vna.connection()
                        self.parent.vna.off()
                    return self.msg_error('PS')

                meas_loop()

                if self.kill:
                    return
        
        else:
            meas_loop()


        def meas_loop():
            if self.parent.sm.box.isChecked():
                self.thread = QThread()
                self.sm_qt = SM_QT()

                self.sm_qt.moveToThread(self.thread)
                V_iSHE = self.thread.started.connect(self.parent.ps.meas)

                self.sm_qt.finished.connect(self.thread.quit)
                self.sm_qt.finished.connect(self.sm_qt.deleteLater)
                self.thread.finished.connect(self.thread.deleteLater)


            if self.parent.vna.box.isChecked():
                try:
                    s_param = self.parent.vna.read_s_param()
                    for s in self.sij:
                        path = os.path.join(self.s_path, s)
                        with open(os.path.join(path, 'Magnitude.txt'), 'a') as f:
                            f.write(str([val for val in getattr(s_param, s)['mag']]) + '\n')
                        
                        with open(os.path.join(path, 'Phase.txt'), 'a') as f:
                            f.write(str([val for val in getattr(s_param, s)['phase']]) + '\n')

                except:
                    self.parent.vna.connection()
                    self.parent.vna.off()
                    try:
                        self.parent.ps.off()
                    except:
                        self.parent.ps.connection()
                        self.parent.ps.off()
                    return self.msg_error('VNA')


            if self.parent.gm.box.isChecked():
                try:
                    H_val = self.parent.gm.read_mag_field()
                    with open(os.path.join(self.path, 'H_values.txt'), 'a') as f:
                            f.write(H_val + '\n')
                    
                except:
                    self.parent.vna.off()
                    self.parent.ps.off()
                    return self.msg_error('GM')
            

            if self.parent.sm.box.isChecked():
                with open(os.path.join(self.path, 'V-iSHE_values.txt'), 'a') as f:
                            f.write(V_iSHE + '\n')


    def msg_error(self, device):
        if device == 'VNA':
            word = 'VNA'
        elif device == 'PS':
            word = 'power supply'
        elif device == 'GM':
            word = 'gaussmeter'
        elif device == 'SM':
            word = 'sourcemeter'

        self.kill = True

        QMessageBox.about(self.parent, 'Warning', f'Connection issue with {word}.')


    def launch_progressbar(self):
        self.okay.setDisabled(True)
        self.time = None
        time_vna = 0
        time_sm = 0

        if self.parent.vna.box.isChecked():
            time_vna = int(self.parent.vna.sw_time.text())

        if self.parent.sm.box.isChecked():
            time_sm = int(self.parent.sm.meas_time.text())

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



    def off(self):
        if self.parent.vna.box.isChecked():
            self.parent.vna.off()

        if self.parent.ps.box.isChecked():
            self.parent.ps.off()

        if self.parent.gm.isChecked():
            self.parent.gm.off()

        if self.parent.sm.isChecked():
            self.parent.sm.off()
