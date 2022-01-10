import os
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import math
import pyvisa as visa
import numpy as np
import matplotlib.pyplot as matplotlib
import time
from VNA import *
from kikusui import *
from gaussmeter import *



class Measures(object):
    def __init__(self, f_start, f_stop, f_point, IFBW, v_start, v_stop, v_step, mag_unit):
        f_start = float(f_start)*1e9
        f_stop = float(f_stop)*1e9
        f_point = int(f_point)
        IFBW = float(IFBW)*1e3
        v_start = float(v_start)
        v_stop = float(v_stop)
        v_step = float(v_step)
        mag_unit = int(mag_unit)
        self.vna = None
        
        rm = visa.ResourceManager()
        rm_list = rm.list_resources()
        
        self.address_gauss = None
        self.address_mag = None
        
        for address in rm_list:
            if address == 'GPIB0::9::INSTR':
                    self.address_gauss = address
            
            elif address == 'GPIB0::3::INSTR':
                    self.address_mag = address
        
        
        if self.address_gauss != None and self.address_mag != None:
            self.gauss = gauss(self.address_gauss, mag_unit)
            self.mag = kikusui(self.address_mag)
            
        elif self.address_gauss != None:
            self.address_gauss = True
        
        elif self.address_mag != None:
            self.address_mag = True
        
            
            
        try:
            self.vna = vna(f_point, f_start, f_stop, IFBW)
            self.mag.start_point(self.v_start)
        except:
            QMessageBox.about(self, "Warning", "Connection issue with VNA")
        
        
        v_point = int((v_stop-v_start)/v_step)+1
        self.v_list = np.linspace(v_start, v_stop, int((v_stop-v_start)/v_step)+1)
        self.H = list(np.zeros_like(self.v_list))
        self.S = list(np.zeros_like(self.v_list)) 
        self.freq = np.linspace(f_start, f_stop, f_point)

        
    
    def getData(self, mag):
        self.mag.set_v(mag)
        return list(self.vna.getData()), self.gauss.getData()
            
        
        
    def reset(self):
        self.mag.off()
        self.vna.reset()



if __name__ == '__main__':
    v_start = 1
    v_stop = 2
    v_step = 0.1
    f_point = 10
    f_start = 100.0e6
    f_stop = 10.0e9
    IFBW = 1000
    
    test = Measures(f_point, f_start, f_stop, IFBW, v_start, v_stop, v_step)
    table = test.getData()
    test.reset()