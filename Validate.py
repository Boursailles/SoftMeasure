import os
import pyvisa as visa
from PyQt5.QtCore import *
import numpy as np
from Save import *
from QTreads import *
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QObject, QThread, pyqtSignal, Qt



class Valid:
    def __init__(self, parent, vna, ps, gm):
        self.parent = parent
        self.vna = vna
        self.ps = ps
        self.gm = gm

        self.kill = False
        self.widget()


    def widget(self):
        self.save = Save()
        self.okay = QPushButton('Okay')
        self.okay.clicked.connect(self.okay_event)

        self.cancel = QPushButton('Close')
        self.cancel.clicked.connect(self.parent.close)

        self.box = QGroupBox('')
        self.box.setFlat(True)

        layout = QGridLayout()

        layout.addWidget(self.save.box, 0, 0)
        layout.addWidget(self.okay, 0, 1)
        layout.addWidget(self.cancel, 0, 2)

        self.box.setLayout(layout)


    def okay_event(self):
        self.path = self.save.pathEdit.text()
        self.folder()
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

        if self.vna.box.isChecked():
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
        
        if self.ps.box.isChecked():
            # Creating current file.
            with open(os.path.join(self.path, 'I_values.txt'), 'w') as f:
                f.write('Current [A]\n')

        if self.gm.box.isChecked():
            # Creating magnetic field file.
            with open(os.path.join(self.path, 'H_values.txt'), 'w') as f:
                f.write('Magnetic Field [' + self.gm.unit.currentText() + ']\n')

        if self.sm.box.isChecked():
            # Creating iSHE voltage file.
            with open(os.path.join(self.path, 'V-iSHE_values.txt'), 'w') as f:
                f.write('iSHE Voltage [V]\n')


    def connection(self):
        self.rm = visa.ResourceManager()

        if self.vna.box.isChecked():
            try:
                self.vna.connection(self.rm)
            except:
                return self.msg_error('VNA')

        if self.ps.box.isChecked():
            try:
                self.ps.connection(self.rm)
            except:
                return self.msg_error('PS')

        if self.gm.box.isChecked():
            try:
                self.gm.connection(self.rm)
            except:
                return self.msg_error('GM')

        if self.sm.box.isChecked():
            try:
                self.sm.connection(self.rm)
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
        if self.vna.box.isChecked():
            try:
                self.vna.initialization()
            except:
                return self.msg_error('VNA')

        if self.ps.box.isChecked():
            try:
                self.ps.initialization()
            except:
                return self.msg_error('PS')

        if self.gm.box.isChecked():
            try:
                self.gm.initialization()
            except:
                # If vna and/or ps are connected, then put them off.
                self.off()
                return self.msg_error('GM')

        if self.sm.box.isChecked():
            try:
                self.sm.initialization()
            except:
                return self.msg_error('SM')


    def meas_record(self):
        if self.ps.box.isChecked():
            amps_list = np.linspace(self.ps.I_start, self.ps.I_stop, self.ps.nb_step)

            for i, amps in enumerate(amps_list):
                try:
                    self.ps.set_current(amps)
                    with open(os.path.join(self.path, 'I_values.txt'), 'a') as f:
                            f.write(str(amps) + '\n')
                
                except:
                    self.ps.connection()
                    self.ps.off()
                    try:
                        self.vna.off()
                    except:
                        self.vna.connection()
                        self.vna.off()
                    return self.msg_error('PS')

                meas_loop()

                if self.kill:
                    return
        
        else:
            meas_loop()


        def meas_loop():
            if self.sm.box.isChecked():
                self.thread = QThread()
                self.sm_qt = SM_QT()

                self.sm_qt.moveToThread(self.thread)
                V_iSHE = self.thread.started.connect(self.ps.meas)

                self.sm_qt.finished.connect(self.thread.quit)
                self.sm_qt.finished.connect(self.sm_qt.deleteLater)
                self.thread.finished.connect(self.thread.deleteLater)


            if self.vna.box.isChecked():
                try:
                    s_param = self.vna.read_s_param()
                    for s in self.sij:
                        path = os.path.join(self.s_path, s)
                        with open(os.path.join(path, 'Magnitude.txt'), 'a') as f:
                            f.write(str([val for val in getattr(s_param, s)['mag']]) + '\n')
                        
                        with open(os.path.join(path, 'Phase.txt'), 'a') as f:
                            f.write(str([val for val in getattr(s_param, s)['phase']]) + '\n')

                except:
                    self.vna.connection()
                    self.vna.off()
                    try:
                        self.ps.off()
                    except:
                        self.ps.connection()
                        self.ps.off()
                    return self.msg_error('VNA')


            if self.gm.box.isChecked():
                try:
                    H_val = self.gm.read_mag_field()
                    with open(os.path.join(self.path, 'H_values.txt'), 'a') as f:
                            f.write(H_val + '\n')
                    
                except:
                    self.vna.off()
                    self.ps.off()
                    return self.msg_error('GM')
            

            if self.sm.box.isChecked():
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





    def off(self):
        if self.vna.box.isChecked():
            self.vna.off()

        if self.ps.box.isChecked():
            self.ps.off()

        if self.gm.isChecked():
            self.gm.off()

        if self.sm.isChecked():
            self.sm.off()
