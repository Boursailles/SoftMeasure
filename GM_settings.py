from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from pyqt_led import Led
import os
import importlib
import glob
import numpy as np



###############################################################################
# This program is working with Interface.py and Validate.py files as parents and files in the GM foler as children for SoftMeasure.
# It contains useful code allowing to operate the GaussMeter (GM).
###############################################################################



class GM_settings:
    def __init__(self):
        """
        Settings of the GM which are generalized for any brand.
        """

        self.instr = None
        self.widget()


    def widget(self):
        """
        Display of GM widgets in the graphics interface.
        """
        
        # File where all parameters in the GUI are saved.
        self.params_path = os.path.join(os.getcwd(), 'GM\parameters.txt')

        if os.path.exists(self.params_path) == False:
            header = 'device\tunit'
            values = str(['0', '0'])[1: -1].replace(', ', '\t')
            with open(self.params_path, 'w') as f:
                f.write(header + '\n' + str(values)[1: -1].replace("'", ""))

        self.params = np.genfromtxt(self.params_path, names=True, delimiter='\t')


        self.box = QGroupBox('GaussMeter')
        self.box.setCheckable(True)


        # Get the list of devices in PS folder.
        list_device = glob.glob('GM/*.py')
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
        self.unit = QComboBox()
        self.unit.addItems(['G', 'T', 'Oe', 'A.m\u207B\u00B9'])
        self.unit.setCurrentIndex(int(self.params['unit']))


        layout = QGridLayout()

        layout.addWidget(QLabel('Device:'), 0, 0)
        layout.addWidget(self.device, 0, 1)
        layout.addWidget(self.led, 0, 2)

        layout.addWidget(QLabel('Unit:'), 1, 0)
        layout.addWidget(self.unit, 1, 1, 1, 2)

        self.box.setLayout(layout)


    def save_params(self):
        """
        Saving of all parameters in order to be used at the next opening.
        """

        header = 'device\tunit'
        values = str([str(self.device.currentIndex()), str(self.unit.currentIndex())])[1: -1].replace(', ', '\t')
        with open(self.params_path, 'w') as f:
            f.write(header + '\n' + str(values)[1: -1].replace("'", ""))


    def connection(self, rm):
        """
        Connection to the chosen GM (see the linked GM file).
        """

        path_device = 'GM.'+ self.device.currentText().replace(' ', '_') + '_GM'
        self.instr = importlib.import_module(path_device).GM(rm)
        self.led.turn_off()

    
    def initialization(self):
        """
        GM initialization with the following parameter (chosen in the interface, see Interface.py):
        self.unit: Number linked to the magnetic field unit.
        """

        self.instr.initialization(self.unit.currentIndex())


    def read_mag_field(self):
        """
        Recording of magnetic field in the variable self.instr.mag_value.
        """
        
        self.instr.read_mag_field()


    def off(self):
        """
        Sets the GM off.
        """

        self.led.turn_off()
