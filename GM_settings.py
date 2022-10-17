from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
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

        layout.addWidget(QLabel('Unit:'), 1, 0)
        layout.addWidget(self.unit, 1, 1)

        self.box.setLayout(layout)


    def connection(self, rm):
        """
        Connection to the chosen GM (see the linked GM file)
        """

        path_device = 'GM.'+ self.device.currentText().replace(' ', '_') + '_GM'
        
        self.instr = importlib.import_module(path_device).GM(rm)

    
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