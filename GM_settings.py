from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from pyqt_led import Led
import os
import importlib
import glob



###############################################################################
# This program is working with Interface.py file for SoftMeasure.
# It contains useful code allowing to operate the GaussMeter (GM).
###############################################################################



class GM_settings:
    def __init__(self):
        """
        Settings of the GM which are generalized for any brand
        """

        self.instr = None
        self.widget()


    def widget(self):
        """
        Display of GM widgets in the graphics interface
        """

        self.box = QGroupBox('GaussMeter')
        self.box.setCheckable(True)
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


        # Get the list of devices in PS folder
        list_device = glob.glob('GM/*.py')
        list_device = [os.path.splitext(val)[0].replace('\\', '/').split('/')[-1].replace('_', ' ')[: -3] for val in list_device]
        
        self.device = QComboBox()
        self.device.addItems(list_device)
        self.device.setCurrentIndex(0)

        self.unit = QComboBox()
        self.unit.addItems(['G', 'T', 'Oe', 'A.m\u207B\u00B9'])
        self.unit.setCurrentIndex(0)


        layout = QGridLayout()

        layout.addWidget(QLabel('Device:'), 0, 0)
        layout.addWidget(self.device, 0, 1)
        layout.addWidget(self.led, 0, 2)

        layout.addWidget(QLabel('Unit:'), 1, 0)
        layout.addWidget(self.unit, 1, 1, 1, 2)

        self.box.setLayout(layout)


    def connection(self, rm):
        """
        Connection to the chosen GM (see the linked GM file)
        """

        path_device = 'GM.'+ self.device.currentText().replace(' ', '_') + '_GM'
        
        self.instr = importlib.import_module(path_device).GM(rm)

        self.led.turn_off()

    
    def initialization(self):
        """
        GM initialization with the following parameter (chosen in the interface, see Interface.py):
        self.unit: Number linked to the magnetic field unit (donner les valeurs)
        """

        self.instr.initialization(self.unit.currentIndex())


    def read_mag_field(self):
        """
        Recording of magnetic field in the variable self.instr.mag_value.
        """
        
        self.instr.read_mag_field()


    def off(self):
        """
        Sets the VNA off.
        """

        self.led.turn_off()
