import pyvisa as visa
from PyQt5.QtWidgets import *
import numpy as np



###############################################################################
# This program is working with GM_settings.py file for SoftMeasure.
# It contains useful code allowing to operate the LakeShore (LS) GaussMeter (GM), model 455 DSP.
###############################################################################



class GM(object):
    def __init__(self, rm):
        """
        LS GM, model 455 DSP

        self.mag_value: Recorded magnetic field value
        """

        self.gm = None
        self.mag_value = None

        # Setup PyVISA instrument
        self.address_gm = 'GPIB0::9::INSTR'

        self.gm = rm.open_resource(self.address_gm)
        print('Connected to ' + self.gm.query("*IDN?"))


    def initialization(self, unit):
        """
        GM initialization

        ---------
        Parameter:
        unit: int
            Number linked to the magnetic field unit (donner les valeurs)
        """

        self.gm.write('UNIT ' + str(unit+1))


    def read_mag_field(self):
        """
        Recording of magnetic field in the variable self.mag_value.
        """

        self.mag_value = self.gm.query("RDGFIELD?")[:-1]

        
        

if __name__ == '__main__':
    test = GM('GPIB0::9::INSTR')
    print(test.gauss_measure())
        
