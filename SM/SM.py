from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from pyqt_led import Led
from time import sleep
import os
import importlib
import glob
import numpy as np



###############################################################################
# This file contain general SourceMeter (SM) settings to display and commands.
###############################################################################



class SETTINGS:
    """Display of the SM settings.
    """
    def __init__(self):
        """Settings widgets for graphics interface of the SM which are generalized for any brand.
        """
        # File where all parameters in the GUI are saved.
        self.params_path = os.path.join(os.getcwd(), 'parameters.txt')

        if os.path.exists(self.params_path) == False:
            header = 'device\tcurrent\tmeasurement_period'
            values = str(['0', '0', '1'])[1: -1].replace(', ', '\t')
            with open(self.params_path, 'w') as f:
                f.write(header + '\n' + str(values)[1: -1].replace("'", ""))

        self.params = np.genfromtxt(self.params_path, names=True, delimiter='\t')


        self.box = QGroupBox('SourceMeter')
        self.box.setCheckable(True)

        # Get the list of devices in VNA folder.
        list_device = glob.glob('Devices/*.py')
        list_device = [os.path.splitext(val)[0].replace('\\', '/').split('/')[-1].replace('_', ' ')[: -3] for val in list_device]
        
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
        self.I = QLineEdit()
        self.I.setText(str(self.params['current']))

        self.meas_time = QLineEdit()
        self.meas_time.setText(str(self.params['measurement_period']))

        layout = QGridLayout()

        layout.addWidget(QLabel('Device:'), 0, 0)
        layout.addWidget(self.device, 0, 1)
        layout.addWidget(self.led, 0, 2)

        layout.addWidget(QLabel('Applied current [A]:'), 1, 0)
        layout.addWidget(self.I, 1, 1, 1, 2)

        layout.addWidget(QLabel('Measurement period [s]:'), 2, 0)
        layout.addWidget(self.meas_time, 2, 1, 1, 2)
        
        
        self.box.setLayout(layout)

    def save_params(self):
        """Saving of all parameters in order to be used at the next opening.
        """
        header = 'device\tcurrent\tmeasurement_period'
        values = str([str(self.device.currentIndex()), self.I.text(), self.meas_time.text()])[1: -1].replace(', ', '\t')
        with open(self.params_path, 'w') as f:
            f.write(header + '\n' + str(values)[1: -1].replace("'", ""))
        

class COMMANDS:
    """Attached commands to the chosen instrument brand in Device directory.
    """
    def __init__(self, settings):
        """Initialiaze entered settings values.

        Args:
            settings (dict): dictionnary of setting values.
        """
        self.settings = settings
        
    def connection(self):
        """Connection to the chosen SM (see the linked SM file).
        """
        path_device = 'SM.'+ self.settings['device'].replace(' ', '_') + '_SM'
        self.instr = importlib.import_module(path_device).SM()
  
    def initialization(self):
        """SM initialization with following parameter (chosen in the interface, see Interface.py):
        self.I: Applied current
        """
        self.instr.initialization(self.settings['I'])
        self.clear_buffer()

    def read_val(self):
        """Recording of voltage value.
        """
        V = self.instr.read_val()
        return V

    def clear_buffer(self):
        """Clearing instrument buffer.
        """
        self.instr.clear_buffer()

    def off(self):
        """Sets the SM off.
        """
        try:
            self.instr.off()
        except NameError:
            pass



if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    win = QWidget()
    win.show()

    sm = SM_settings()
    sm.connection('Keithley 2450 SM')
    sm.initialization()

    sys.exit(app.exec_())