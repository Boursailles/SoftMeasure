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
        rm_list = rm.list_resources()
        print(rm_list)
        address_vna = "TCPIP0::169.254.126.124::inst0::INSTR"
        self.VNA = rm.open_resource(address_vna)
        print('Connected to '+ self.VNA.query("*IDN?"))

        self.VNA.write("*RST")
        
        # Define name trace with S parameter
        self.VNA.write("CALC1:PAR:SDEF 'Trc1', 'S11'")
        self.VNA.write("CALC2:PAR:SDEF 'Trc2', 'S12'")
        self.VNA.write("CALC3:PAR:SDEF 'Trc3', 'S21'")
        self.VNA.write("CALC4:PAR:SDEF 'Trc4', 'S22'")
        
        
        # Define logarithmic scale
        self.VNA.write("CALC1:FORM MLOG")
        self.VNA.write("CALC2:FORM MLOG")
        self.VNA.write("CALC3:FORM MLOG")
        self.VNA.write("CALC4:FORM MLOG")
        
        
        # Display 4 windows
        self.VNA.write("DISP:WIND1:STAT ON")
        self.VNA.write("DISP:WIND2:STAT ON")
        self.VNA.write("DISP:WIND3:STAT ON")
        self.VNA.write("DISP:WIND4:STAT ON")
        
        
        # Display each trace to each window
        self.VNA.write("DISP:WIND1:TRAC1:FEED 'Trc1'")
        self.VNA.write("DISP:WIND2:TRAC2:FEED 'Trc2'")
        self.VNA.write("DISP:WIND3:TRAC3:FEED 'Trc3'")
        self.VNA.write("DISP:WIND4:TRAC4:FEED 'Trc4'")
        
        
        # Auto-scale Y-axis
        self.VNA.write("DISP:TRAC1:Y:AUTO ONCE, 'Trc1'")
        self.VNA.write("DISP:TRAC2:Y:AUTO ONCE, 'Trc2'")
        self.VNA.write("DISP:TRAC3:Y:AUTO ONCE, 'Trc3'")
        self.VNA.write("DISP:TRAC4:Y:AUTO ONCE, 'Trc4'")
        
        
        # Measures settings
        self.VNA.write("SWE:POIN " + str(self.n_point))
        self.VNA.write("SENS:FREQ:STAR " + str(self.f_start))
        self.VNA.write("SENS:FREQ:STOP " + str(self.f_stop))
        self.VNA.write("SENS:BWID " + str(self.IFBW))
        
        
        self.VNA.write("INIT:CONT:ALL ON")
    
        
        
        
        
    def reset(self):
        self.VNA.write("SENS:HOLD:FUNC CONT")
        self.VNA.write("SENS:BWID 1000")
        
        
        
        
if __name__ == '__main__':
    n_point = 5
    f_start = 100.0e6
    f_stop = 8.0e9
    IFBW = 1000
    
    test = vna(n_point, f_start, f_stop, IFBW)