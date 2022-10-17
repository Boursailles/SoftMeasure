from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import os
import importlib
import glob



###############################################################################
# This program is working with Interface.py file for SoftMeasure.
# It contains useful code allowing to operate the Vector Network Analyzer (VNA).
###############################################################################



class VNA_settings():
    def __init__(self):
        """
        Settings of the VNA which are generalized for any brand
        """

        self.instr = None
        self.widget()


    def widget(self):
        """
        Display of VNA widgets in the graphics interface
        """

        self.box = QGroupBox('Vector Network Analyzer')
        self.box.setCheckable(True)

        # Get the list of devices in PS folder
        list_device = glob.glob('VNA/*.py')
        list_device = [os.path.splitext(val)[0].replace('\\', '/').split('/')[-1].replace('_', ' ')[: -4] for val in list_device]
        
        self.device = QComboBox()
        self.device.addItems(list_device)
        self.device.setCurrentIndex(0)

        self.f_start = QLineEdit()
        self.f_stop = QLineEdit()
        self.nb_step = QSpinBox()
        self.nb_step.setMaximum(10000)
        self.nb_step.setValue(2)
        self.IFBW = QLineEdit()
        self.power = QComboBox()
        self.power.addItems(['-10', '0', '10'])
        self.power.setCurrentIndex(0)
        

        layout = QGridLayout()

        layout.addWidget(QLabel('Device:'), 0, 0)
        layout.addWidget(self.device, 0, 1)

        layout.addWidget(QLabel('Start [GHz]:'), 1, 0)
        layout.addWidget(self.f_start, 1, 1)

        layout.addWidget(QLabel('Stop [GHz]:'), 2, 0)
        layout.addWidget(self.f_stop, 2, 1)

        layout.addWidget(QLabel('Values number:'), 3, 0)
        layout.addWidget(self.nb_step, 3, 1)

        layout.addWidget(QLabel('IFBW [kHz]:'), 4, 0)
        layout.addWidget(self.IFBW, 4, 1)

        layout.addWidget(QLabel('Power [dBm]:'), 5, 0)
        layout.addWidget(self.power, 5, 1)

        self.box.setLayout(layout)


    def connection(self, rm):
        """
        Connection to the chosen VNA (see the linked VNA file)

        ---------
        Parameter:
        rm: class
            Ressource Manager
        """

        path_device = 'VNA.'+ self.device.currentText().replace(' ', '_') + '_VNA'
        
        self.instr = importlib.import_module(path_device).VNA(rm)

    
    def initialization(self):
        """
        VNA initialization with following parameters (chosen in the interface, see Interface.py):
        self.f_start: Starting frequency
        self.f_stop: Stopping frequency
        self.nb_step: Step number
        self.IFBW: Intermediate Frequency Band Width
        self.power: Signal power
        """

        self.instr.initialization(self.f_start.text(), self.f_stop.text(), self.nb_step.text(), self.IFBW.text(), self.power.currentText())


    def read_s_param(self):
        """
        Recording of S-parameters in the following dictionaries:
        self.instr.s11
        self.instr.s12
        self.instr.s21
        self.instr.s22

        Each are sorted like:
        self.instr.sij = {'dB': array, 'phase': array}
        """
        
        self.instr.read_s_param()


    def off(self):
        """
        Sets the VNA off.
        """
        self.instr.off()





if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    win = QWidget()
    win.show()

    vna = VNA_settings()
    vna.connection('RS ZNB40 VNA')
    vna.initialization()

    sys.exit(app.exec_())