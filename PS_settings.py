from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import importlib



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

        self.PS_box = QGroupBox('Power Supply')
            
        self.I_start = QLineEdit()
        self.I_stop = QLineEdit()
        self.nb_step = QSpinBox()
        self.nb_step.setMaximum(10000)
        self.nb_step.setValue(2)
        # The following is to put in a section "Gauss-meter"
        """self.unit = QComboBox()
        self.unit.addItems(['G', 'T', 'Oe', 'A.m\u207B\u00B9'])
        self.unit.setCurrentIndex(1)"""
        # Faire le bouton choix du PS: Dan ou Anritsu
            
        PS_layout = QGridLayout()
        
        # Section "Gauss-meter"
        """PS_layout.addWidget('Unit:', 0, 0)
        PS_layout.addWidget(self.unit, 0, 1)"""

        PS_layout.addWidget(QLabel('Start [A]:'), 1, 0)
        PS_layout.addWidget(self.I_start, 1, 1)
            
        PS_layout.addWidget(QLabel('Stop [A]:'), 2, 0)
        PS_layout.addWidget(self.I_stop, 2, 1)
            
        PS_layout.addWidget(QLabel('Values number:'), 3, 0)
        PS_layout.addWidget(self.nb_step, 3, 1)
            
        self.PS_box.setLayout(PS_layout)


    def connection(self, ps):
        """
        Connection to the chosen PS (see the linked PS file)

        ---------
        Parameter:
        ps: str
            File name of the chosen PS
        """

        self.instr = importlib.__import__('PS/' + ps.replace(' ', '_')).PS()

    
    def initialization(self):
        """
        PS initialization.
        """

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