import os
import sys
import math
import pyvisa as visa
import numpy as np
#import matplotlib.pyplot as matplotlib
import time
from gaussmeter import *


class kikusui(object):
    def __init__(self, address_mag):
        self.magnet = None
        self.address_mag = address_mag
        
        rm = visa.ResourceManager()
        self.magnet = rm.open_resource(self.address_mag)
        print('Connected to ' + self.magnet.query("*IDN?"))
        self.magnet.write("*RST")
    
    
    
    def start_point(self, v_start):
        self.magnet.write("OUTP:STAT:IMM ON")
        self.magnet.write("SOUR:VOLT:LEV:IMM:AMPL " + str(v_start))
        time.sleep(5)


    def set_v(self, volt):
        self.magnet.write("SOUR:VOLT:LEV:IMM:AMPL " + str(volt))
        time.sleep(5)


    def off(self):
        self.magnet.write("SOUR:VOLT:LEV:IMM:AMPL 0")
        time.sleep(5)
        self.magnet.write("OUTP:STAT:IMM OFF")
        


if __name__ == '__main__':
    address_mag="GPIB1::3::INSTR"
    v_start = 5
    volt = 4.9

    test = kikusui(address_mag, v_start, volt)
    test.set_mag()
    test.mag_off()