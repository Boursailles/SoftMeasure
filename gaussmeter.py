import os
import sys
import pyvisa as visa
import numpy as np



class gauss(object):
    def __init__(self, address_gauss, unit):
        rm = visa.ResourceManager()
        self.gauss = rm.open_resource(address_gauss)
        self.gauss.write('UNIT ' + str(unit+1))
        print(unit+1)
        print('Connected to ' + self.gauss.query("*IDN?"))


    def getData(self):
        value = self.gauss.query("RDGFIELD?")[:-1]
        return value
        
        

if __name__ == '__main__':
    test = gauss('GPIB0::9::INSTR')
    print(test.gauss_measure())
        
