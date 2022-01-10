from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import numpy as np
import matplotlib.pyplot as plt
from measures import *
from tab1_signals import *
from Save import *



class tab1(tab1_signals, save):
    # First tab
    def __init__(self):
        self.params = np.loadtxt(os.getcwd()+'/parameters', dtype='str')
        
        self.tab1 = QWidget()
        
        self.freq_box()
        self.volt_box()
        self.mag_box()
        self.launch_box()
        self.okay = QPushButton('Okay')
        
        self.tab1_layout = QGridLayout()
        
        self.tab1_layout.addWidget(QLabel(''), 0, 0)
        self.tab1_layout.addWidget(self.f_box, 1, 0, 4, 1)
        
        self.tab1_layout.addWidget(QLabel(''), 5, 0)
        self.tab1_layout.addWidget(self.v_box, 6, 0, 3, 1)
        
        self.tab1_layout.addWidget(QLabel(''), 0, 1)
        self.tab1_layout.addWidget(self.m_box, 1, 1)
        
        self.tab1_layout.addWidget(QLabel(''), 2, 1)
        self.tab1_layout.addWidget(self.l_box, 4, 1)
        
        self.tab1_layout.addWidget(QLabel(''), 5, 1)
        self.tab1_layout.addWidget(self.okay, 6, 1)
        
        self.tab1.setLayout(self.tab1_layout)
        
        
        super().__init__(self.pathEdit, self.okay, self.f_start, self.f_stop, self.f_point, self.IFBW,\
            self.v_start, self.v_stop, self.v_step, self.mag_unit, self.initialize, self.loading, self.end)
        
        
        
    def freq_box(self):
        # Frequency settings
        self.f_box = QGroupBox('Frequency settings')
        
        self.f_start = QLineEdit(self.params[0])
        self.f_stop = QLineEdit(self.params[1])
        self.f_point = QSpinBox()
        self.f_point.setMaximum(10000)
        self.f_point.setValue(int(self.params[2]))
        self.IFBW = QLineEdit(self.params[3])
        
        
        freq_layout = QGridLayout()
        
        freq_layout.addWidget(QLabel('Start [GHz] :'), 0, 0)
        freq_layout.addWidget(self.f_start, 0, 1)
        
        freq_layout.addWidget(QLabel('Stop [GHz] :'), 1, 0)
        freq_layout.addWidget(self.f_stop, 1, 1)
        
        freq_layout.addWidget(QLabel('Values number :'), 2, 0)
        freq_layout.addWidget(self.f_point, 2, 1)
        
        freq_layout.addWidget(QLabel('IFBW [kHz] :'), 3, 0)
        freq_layout.addWidget(self.IFBW, 3, 1)
        
        self.f_box.setLayout(freq_layout)
        
        
        
    def volt_box(self):
        # Voltage settings
        self.v_box = QGroupBox('Voltage settings')
            
        self.v_start = QLineEdit(self.params[4])
        self.v_stop = QLineEdit(self.params[5])
        self.v_step = QLineEdit(self.params[6])
            
            
        volt_layout = QGridLayout()
            
        volt_layout.addWidget(QLabel('Start [V] :'), 0, 0)
        volt_layout.addWidget(self.v_start, 0, 1)
            
        volt_layout.addWidget(QLabel('Stop [V] :'), 1, 0)
        volt_layout.addWidget(self.v_stop, 1, 1)
            
        volt_layout.addWidget(QLabel('Step [V] :'), 2, 0)
        volt_layout.addWidget(self.v_step, 2, 1)
            
        self.v_box.setLayout(volt_layout)
        


    def mag_box(self):
        # Magnetics field unit
        self.m_box = QGroupBox('Magnetic field setting')
        self.mag_unit = QComboBox()
        self.mag_unit.addItems(['G', 'T', 'Oe', 'A.m\u207B\u00B9'])
        self.mag_unit.setCurrentIndex(int(self.params[7]))
        
        
        mag_layout = QFormLayout()
        mag_layout.addRow('Unit :', self.mag_unit)
        
        self.m_box.setLayout(mag_layout)
        
        
        
    def launch_box(self):
        # Launch settings
        self.l_box = QGroupBox('Launch settings')
        launch_layout = QHBoxLayout()
        save.__init__(self, launch_layout)
        
        self.l_box.setLayout(launch_layout)
        
        
    
    def initialize(self):
        self.space = QLabel('')
        self.pb = QProgressBar()
        
        self.pb.setMinimum(0)
        self.pb.setMaximum(len(self.v_list))
        self.pb.setValue(0)
        estimation_h = str((len(self.v_list)*3+10)//3600)
        estimation_m = str(((len(self.v_list)*3+10)%3600)//60)
        
        self.estimation_time = QLabel('Estimated time : '+estimation_h+'h'+estimation_m)
        
        self.tab1_layout.addWidget(self.pb, 7, 1)
        
        self.tab1_layout.addWidget(self.estimation_time, 8, 1)
        
        self.tab1.setLayout(self.tab1_layout)
        self.okay.setEnabled(False)
        self.tab1.update()
        self.app.processEvents()
        
        
        
    def loading(self, val):
        self.pb.setValue(val)

        estimation_h = str(((len(self.v_list) - val)*8+10)//3600)
        estimation_m = str((((len(self.v_list) - val)*8+10)%3600)//60)
        
        self.estimation_time.setText('Estimated time : '+estimation_h+'h'+estimation_m)
        self.estimation_time.update()
        self.pb.update()
        self.tab1.update()
        self.app.processEvents()
    
    
    
    def end(self):
        
        self.tab1_layout.removeWidget(self.pb)
        self.tab1_layout.removeWidget(self.estimation_time)
        self.pb.deleteLater()
        self.okay.setEnabled(True)
        self.estimation_time.deleteLater()
        
        
        
if __name__ == '__main__':
    test = tab1()  