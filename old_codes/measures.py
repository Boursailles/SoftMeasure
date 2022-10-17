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
from RS_VNA import RSZNB40VNA
from kikusui import *
from gaussmeter import *
from danfysik9700 import *



class Measures(object):
    def __init__(self, f_start, f_stop, f_point, IFBW, v_start, v_stop, v_step, mag_unit):
        self.fstart = float(f_start)*1e9
        self.fstop = float(f_stop)*1e9
        self.fpoint = int(f_point)
        self.IFBW2 = float(IFBW)*1e3
        self.vstart = float(v_start)
        self.vstop = float(v_stop)
        self.vstep = float(v_step)
        mag_unit = int(mag_unit)
        self.vna = None
        
        rm = visa.ResourceManager()
        rm_list = rm.list_resources()
        
        self.address_gauss = None
        self.address_mag = None
        
        for address in rm_list:
            if address == 'GPIB0::9::INSTR':
                    self.address_gauss = address
            
            #elif address == 'GPIB0::3::INSTR':
                    #self.address_mag = address
                    
            elif address == 'ASRL1::INSTR':
                    self.address_mag = address
        
        print(self.address_gauss)
        print(self.address_mag)
        
        
        if self.address_gauss != None and self.address_mag != None:
            self.gauss = gauss(self.address_gauss, mag_unit)
            #self.mag = kikusui(self.address_mag)
            self.mag = danfysik9700()
            #DanWithTau()
            
        elif self.address_gauss != None:
            self.address_gauss = True
        
        elif self.address_mag != None:
            self.address_mag = True
                   
        try:
            self.vna = RSZNB40VNA(self.fpoint, self.fstart, self.fstop, self.IFBW2)
            #self.mag.start_point(self.v_start)
            self.mag.set(self.vstart)
        except Exception as err:
            error_str = "{0}".format(err)
            print(error_str)
            QMessageBox.about(self, "Warning", "Connection issue with VNA")
                    
        
        self.v_list = np.linspace(self.vstart, self.vstop, int((self.vstop-self.vstart)/self.vstep)+1)
        self.H = list(np.zeros_like(self.v_list))
        self.S = list(np.zeros_like(self.v_list)) 
        self.freq = np.linspace(self.fstart, self.fstop, self.fpoint)      
    
    def getData(self, mag):
        #self.mag.set_v(mag)
        print('1')
        self.mag.set(mag)
        print('2')
        return list(self.vna.read_s_param()), self.gauss.getData()
        
    def reset(self):
        self.mag.off()
        #self.vna.reset()


if __name__ == '__main__':
    v_start = 1
    v_stop = -1
    v_step = 0.1
    f_point = 10
    f_start = 100.0e6
    f_stop = 10.0e9
    IFBW = 1000
    
    test = Measures(f_point, f_start, f_stop, IFBW, v_start, v_stop, v_step)
    table = test.getData()
    test.reset()