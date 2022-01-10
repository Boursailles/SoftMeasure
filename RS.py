import os
import sys
import math
import pyvisa as visa
import numpy as np
import matplotlib.pyplot as matplotlib
import time

class vna(object):
    def __init__(self, n_point, f_start, f_stop, IFBW):
        self.n_point = n_point
        self.f_start = f_start
        self.f_stop = f_stop
        self.IFBW = IFBW
        
        rm = visa.ResourceManager()
        
        address_vna = "TCPIP0::169.254.126.124::inst0::INSTR"
        self.VNA = rm.open_resource(address_vna)
        print('Connected to '+ self.VNA.query("*IDN?"))

        self.VNA.write("*RST")
        
        
        # Define name trace with S parameter
        self.VNA.write("CALC:PAR:SDEF 'Trc1', 'S11'")
        self.VNA.write("CALC:PAR:SDEF 'Trc2', 'S12'")
        self.VNA.write("CALC:PAR:SDEF 'Trc3', 'S21'")
        self.VNA.write("CALC:PAR:SDEF 'Trc4', 'S22'")
        
        self.VNA.write("CALC:PAR:SDEF 'Trc5', 'S11'")
        self.VNA.write("CALC:FORM PHAS")
        self.VNA.write("CALC:PAR:SDEF 'Trc6', 'S12'")
        self.VNA.write("CALC:FORM PHAS")
        self.VNA.write("CALC:PAR:SDEF 'Trc7', 'S21'")
        self.VNA.write("CALC:FORM PHAS")
        self.VNA.write("CALC:PAR:SDEF 'Trc8', 'S22'")
        self.VNA.write("CALC:FORM PHAS")
        
        
        # Display 4 windows
        self.VNA.write("DISP:WIND1:STAT ON")
        self.VNA.write("DISP:WIND2:STAT ON")
        self.VNA.write("DISP:WIND3:STAT ON")
        self.VNA.write("DISP:WIND4:STAT ON")
        
        self.VNA.write("DISP:WIND5:STAT ON")
        self.VNA.write("DISP:WIND6:STAT ON")
        self.VNA.write("DISP:WIND7:STAT ON")
        self.VNA.write("DISP:WIND8:STAT ON")
        
        
        # Display each trace to each window
        self.VNA.write("DISP:WIND1:TRAC:FEED 'Trc1'")
        self.VNA.write("DISP:WIND2:TRAC:FEED 'Trc2'")
        self.VNA.write("DISP:WIND3:TRAC:FEED 'Trc3'")
        self.VNA.write("DISP:WIND4:TRAC:FEED 'Trc4'")
        
        self.VNA.write("DISP:WIND5:TRAC:FEED 'Trc5'")
        self.VNA.write("DISP:WIND6:TRAC:FEED 'Trc6'")
        self.VNA.write("DISP:WIND7:TRAC:FEED 'Trc7'")
        self.VNA.write("DISP:WIND8:TRAC:FEED 'Trc8'")
        
        
        # Auto-scale Y-axis
        self.VNA.write("DISP:TRAC1:Y:AUTO ONCE, 'Trc1'")
        self.VNA.write("DISP:TRAC2:Y:AUTO ONCE, 'Trc2'")
        self.VNA.write("DISP:TRAC3:Y:AUTO ONCE, 'Trc3'")
        self.VNA.write("DISP:TRAC4:Y:AUTO ONCE, 'Trc4'")
        
        
        
        # Measures settings
        self.VNA.write("SWE:POIN " + str(self.n_point))
        self.VNA.write("FREQ:STAR " + str(self.f_start))
        self.VNA.write("FREQ:STOP " + str(self.f_stop))
        self.VNA.write("BWID " + str(self.IFBW))

        self.VNA.write("INIT:CONT:ALL ON")

    def getData(self):
        
        self.VNA.write("INIT:CONT:ALL OFF")
        
        self.VNA.write("INIT:IMM:SCOPE ALL")
        
        
        self.VNA.write("SWEEP:COUNT:ALL 1")
        self.VNA.write("INIT:IMM; *WAI")
        
        self.VNA.timeout = 10000000
        
        self.VNA.write("INIT:CONT:ALL ON")
        
        self.VNA.write("DISP:TRAC1:Y:AUTO ONCE, 'Trc1'")
        self.VNA.write("DISP:TRAC2:Y:AUTO ONCE, 'Trc2'")
        self.VNA.write("DISP:TRAC3:Y:AUTO ONCE, 'Trc3'")
        self.VNA.write("DISP:TRAC4:Y:AUTO ONCE, 'Trc4'")
        
        freq = np.linspace(self.f_start, self.f_stop, self.n_point)
        
        
        
        self.VNA.write("FORM:DATA ASCii")
        
        
        s11_dB = self.VNA.query("CALC:DATA:TRAC? 'Trc1', FDAT")[:-1]
        s11_phase = self.VNA.query("CALC:DATA:TRAC? 'Trc5', FDAT")[:-1]
        
        s12_dB = self.VNA.query("CALC:DATA:TRAC? 'Trc2', FDAT")[:-1]
        s12_phase = self.VNA.query("CALC:DATA:TRAC? 'Trc6', FDAT")[:-1]
        
        s21_dB = self.VNA.query("CALC:DATA:TRAC? 'Trc3', FDAT")[:-1]
        s21_phase = self.VNA.query("CALC:DATA:TRAC? 'Trc7', FDAT")[:-1]
        
        s22_dB = self.VNA.query("CALC:DATA:TRAC? 'Trc4', FDAT")[:-1]
        s22_phase = self.VNA.query("CALC:DATA:TRAC? 'Trc8', FDAT")[:-1]
        
        
        s11_dB = [float(val) for val in s11_dB.split(',')]
        s11_phase = [float(val) for val in s11_phase.split(',')]
        
        s12_dB = [float(val) for val in s12_dB.split(',')]
        s12_phase = [float(val) for val in s12_phase.split(',')]
        
        s21_dB = [float(val) for val in s21_dB.split(',')]
        s21_phase = [float(val) for val in s21_phase.split(',')]
        
        s22_dB = [float(val) for val in s22_dB.split(',')]
        s22_phase = [float(val) for val in s22_phase.split(',')]
        
        
        s11 = np.array([s11_dB, s11_phase])
        s12 = np.array([s12_dB, s12_phase])
        s21 = np.array([s21_dB, s21_phase])
        s22 = np.array([s22_dB, s22_phase])
    
        return s11, s12, s21, s22
        
        
        
if __name__ == '__main__':
    n_point = 3001
    f_start = 100.0e6
    f_stop = 8.0e9
    IFBW = 1000
    
    test = vna(n_point, f_start, f_stop, IFBW)
    test.getData()