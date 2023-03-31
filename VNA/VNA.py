from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from pyqt_led import Led
import os
import importlib
import glob
import numpy as np



###############################################################################
# This file contain general Vector Network Analyzer (VNA) settings to display and commands.
###############################################################################



class SETTINGS:
    """Display of the VNA settings.
    """
    def __init__(self):
        """Settings widgets for graphics interface of the VNA which are generalized for any brand.
        """
        # File where all parameters in the GUI are saved.
        self.params_path = os.path.join(os.getcwd(), 'VNA\parameters.txt')

        if os.path.exists(self.params_path) == False:
            header = 'device\tstarting_frequency\tending_frequency\tstep_number\tIFBW\tpower'
            values = str(['0', '0', '1', '2', '1', '0'])[1: -1].replace(', ', '\t')
            with open(self.params_path, 'w') as f:
                f.write(header + '\n' + str(values)[1: -1].replace("'", ""))

        self.params = np.genfromtxt(self.params_path, names=True, delimiter='\t')

        self.box = QGroupBox('Vector Network Analyzer')
        self.box.setCheckable(True)

        # Get the list of devices in VNA folder.
        list_device = glob.glob('VNA/*.py')
        list_device = [os.path.splitext(val)[0].replace('\\', '/').split('/')[-1].replace('_', ' ')[: -4] for val in list_device]
        
        self.device = QComboBox()
        self.device.addItems(list_device)
        self.device.setCurrentIndex(int(self.params['device']))

        # Creation of a led in order to indicate if the instrument is connected or not.
        self.led = Led(self, shape=Led.circle, off_color=Led.red, on_color=Led.green)
        self.led.setFixedSize(self, 16)
        self.led.turn_off()

        def checkBoxChangedAction():
            if self.box.isChecked():
                self.led.set_off_color(Led.red)
                self.led.turn_off()
            else:
                self.led.set_off_color(Led.black)
                self.led.turn_off()
        
        self.box.toggled.connect(checkBoxChangedAction)

        # Creation of all parameters in the GUI.
        self.f_start = QLineEdit()
        self.f_start.setText(str(self.params['starting_frequency']))

        self.f_stop = QLineEdit()
        self.f_stop.setText(str(self.params['ending_frequency']))

        self.nb_step = QSpinBox()
        self.nb_step.setMaximum(10000)
        self.nb_step.setValue(int(self.params['step_number']))

        self.IFBW = QLineEdit()
        self.IFBW.setText(str(self.params['IFBW']))

        self.power = QComboBox()
        self.power.addItems(['-10', '0', '10'])
        self.power.setCurrentIndex(int(self.params['power']))
        

        layout = QGridLayout()

        layout.addWidget(QLabel('Device:'), 0, 0)
        layout.addWidget(self.device, 0, 1)
        layout.addWidget(self.led, 0, 2)

        layout.addWidget(QLabel('Start [GHz]:'), 1, 0)
        layout.addWidget(self.f_start, 1, 1, 1, 2)

        layout.addWidget(QLabel('Stop [GHz]:'), 2, 0)
        layout.addWidget(self.f_stop, 2, 1, 1, 2)

        layout.addWidget(QLabel('Values number:'), 3, 0)
        layout.addWidget(self.nb_step, 3, 1, 1, 2)

        layout.addWidget(QLabel('IFBW [kHz]:'), 4, 0)
        layout.addWidget(self.IFBW, 4, 1, 1, 2)

        layout.addWidget(QLabel('Power [dBm]:'), 5, 0)
        layout.addWidget(self.power, 5, 1, 1, 2)

        self.box.setLayout(layout)

    def save_params(self):
        """Saving of all parameters in order to be used at the next opening.
        """
        
        header = 'device\tstarting_frequency\tending_frequency\tstep_number\tIFBW\tpower'
        values = str([str(self.device.currentIndex()), self.f_start.text(), self.f_stop.text(), self.nb_step.text(), self.IFBW.text(), str(self.power.currentIndex())])[1: -1].replace(', ', '\t')
        with open(self.params_path, 'w') as f:
            f.write(header + '\n' + str(values)[1: -1].replace("'", ""))


class COMMANDS:
    """Attached commands to the chosen instrument brand in SM directory.
    """
    def __init__(self, settings):
        """Initialiaze entered settings values.

        Args:
            settings (dict): dictionnary of setting values.
        """
        self.settings = settings
    
    def connection(self):
        """Connection to the chosen VNA (see the linked VNA file).
        """
        path_device = 'VNA.'+ self.settings['device'].replace(' ', '_') + '_VNA'
        self.instr = importlib.import_module(path_device).VNA()
        self.led.turn_on()
 
    def initialization(self):
        """VNA initialization with following parameters (chosen in the interface, see Interface.py):
        self.IFBW: Intermediate Frequency Band Width
        self.power: Signal power
        """
        self.instr.initialization(self.settings['IFBW'], self.settings['power'])

    def meas_settings(self, nb_point, f_start, f_stop):
        """Change VNA settings.

        Args:
            nb_point (str): Number of steps.
            f_start (str): Start frequency.
            f_stop (str): Stop frequency.
        """
        self.instr.meas_settings(nb_point, f_start, f_stop)

    def read_s_param(self):
        """Recording of S-parameters in the following dictionaries:
        self.instr.s11
        self.instr.s12
        self.instr.s21
        self.instr.s22

        Each are sorted like:
        self.instr.sij = {'Magnitude': array, 'Phase': array}
        """
        self.instr.read_s_param()



if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    win = QWidget()
    win.show()

    vna = VNA_settings()
    vna.connection('RS ZNB40 VNA')
    vna.initialization()

    sys.exit(app.exec_())