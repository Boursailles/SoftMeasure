from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from pyqt_led import Led
import importlib
import glob
import os
import numpy as np



###############################################################################
# This file contain general Power Supply (PS) settings to display and commands.
###############################################################################



class SETTINGS:
    """Display of the PS settings.
    """
    def __init__(self):
        """Settings widgets for graphics interface of the PS which are generalized for any brand.
        """
        # Current considered as high, in amperes.
        self.I_high = 16
        # File where all parameters in the GUI are saved.
        self.params_path = os.path.join(os.getcwd(), 'PS/parameters.txt')

        if os.path.exists(self.params_path) == False:
            header = 'device\tstarting_current\tending_current\tstep_number'
            values = str(['0', '0', '1', '2'])[1: -1].replace(', ', '\t')
            with open(self.params_path, 'w') as f:
                f.write(header + '\n' + str(values)[1: -1].replace("'", ""))

        self.params = np.genfromtxt(self.params_path, names=True, delimiter='\t')
        
        self.box = QGroupBox('Power Supply')
        self.box.setCheckable(True)
        
        
        # Get the list of devices in PS folder.
        list_device = glob.glob('PS/Devices/*.py')
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
        self.I_start = QLineEdit()
        self.I_start.setText(str(self.params['starting_current']))

        self.I_stop = QLineEdit()
        self.I_stop.setText(str(self.params['ending_current']))

        self.nb_step = QSpinBox()
        self.nb_step.setMaximum(10000)
        self.nb_step.setValue(int(self.params['step_number']))
        

        layout = QGridLayout()        

        layout.addWidget(QLabel('Device:'), 0, 0)
        layout.addWidget(self.device, 0, 1)
        layout.addWidget(self.led, 0, 2)

        layout.addWidget(QLabel('Start [A]:'), 1, 0)
        layout.addWidget(self.I_start, 1, 1, 1, 2)
            
        layout.addWidget(QLabel('Stop [A]:'), 2, 0)
        layout.addWidget(self.I_stop, 2, 1, 1, 2)
            
        layout.addWidget(QLabel('Values number:'), 3, 0)
        layout.addWidget(self.nb_step, 3, 1, 1, 2)
            
        self.box.setLayout(layout)

    def save_params(self):
        """Saving of all parameters in order to be used at the next opening.
        """
        header = 'device\tstarting_current\tending_current\tstep_number'
        values = str([str(self.device.currentIndex()), self.I_start.text(), self.I_stop.text(), self.nb_step.text()])[1: -1].replace(', ', '\t')
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
        """Connection to the chosen PS (see the linked PS file).
        """
        path_device = 'PS.'+ self.settings['device'].replace(' ', '_') + '_PS'
        self.instr = importlib.import_module(path_device).PS()
        
        # An error is occured if the chosen current is higher than the possible one.
        assert max(abs(self.settings['I_start']), abs(self.settings['I_stop'])) > self.instr.I_max, f"The supplied current is higher than the maximal one ($I = {self.instr.I_max} A$) supported by the device {self.settings['device']}."
        
        # Warning message.
        self.cooling_circuit_msg()

    def initialization(self):
        """PS initialization.
        """
        self.instr.initialization()

    def set_current(self, amps):
        """PS setting current in Amps.
        """
        self.instr.set_current(amps)
  
    def off(self):
        """Sets the PS off.
        """
        self.instr.off()

    def cooling_circuit_msg(self):
        """Warning message for the cooling circuit.
        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText('Please, be careful!')
        msg.setInformativeText("Don't forget to start the cooling circuit.")
        msg.setWindowTitle("Warning")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()