from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import importlib
import glob
import os
import sys



###############################################################################
# This program is working with Interface.py file for SoftMeasure.
# It contains useful code allowing to operate the Power Supply (PS).
###############################################################################



class PS_settings():
    def __init__(self):
        """
        Settings of the PS which are generalized for any brand
        """

        self.instr = None
        self.widget()


    def widget(self):
        """
        Display of PS widgets in the graphics interface
        """

        self.box = QGroupBox('Power Supply')
        self.box.setCheckable(True)
        
        
        # Get the list of devices in PS folder
        list_device = glob.glob('PS/*.py')
        list_device = [os.path.splitext(val)[0].replace('\\', '/').split('/')[-1].replace('_', ' ')[: -3] for val in list_device]
        
        self.device = QComboBox()
        self.device.addItems(list_device)
        self.device.setCurrentIndex(0)

        self.I_start = QLineEdit()
        self.I_stop = QLineEdit()
        self.nb_step = QSpinBox()
        self.nb_step.setMaximum(10000)
        self.nb_step.setValue(2)
        

        layout = QGridLayout()

        layout.addWidget(QLabel('Device:'), 0, 0)
        layout.addWidget(self.device, 0, 1)

        layout.addWidget(QLabel('Start [A]:'), 1, 0)
        layout.addWidget(self.I_start, 1, 1)
            
        layout.addWidget(QLabel('Stop [A]:'), 2, 0)
        layout.addWidget(self.I_stop, 2, 1)
            
        layout.addWidget(QLabel('Values number:'), 3, 0)
        layout.addWidget(self.nb_step, 3, 1)
            
        self.box.setLayout(layout)


    def connection(self, rm):
        """
        Connection to the chosen PS (see the linked PS file)
        """

        path_device = 'PS.'+ self.device.currentText().replace(' ', '_') + '_PS'
        
        self.instr = importlib.import_module(path_device).PS(rm)

    
    def initialization(self):
        """
        PS initialization.
        """

        QMessageBox.about(self, 'Reminder', 'Is the cooling system on?')
        self.instr.initialization()


    def set_current(self, amps):
        """
        PS setting current in Amps.
        """
        self.instr.set_current(amps)

    
    def off(self):
        """
        Sets the PS off.
        """
        self.instr.off()