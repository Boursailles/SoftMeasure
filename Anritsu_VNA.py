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
        address_vna = "TCPIP0::169.254.239.174::INSTR"
        self.VNA = rm.open_resource(address_vna)
        print('Connected to '+ self.VNA.query("*IDN?"))

        #VNA.write("*RST")
        self.VNA.write("CALC1:PAR1:FORM LOGPH")
        self.VNA.write("CALC1:PAR2:FORM LOGPH")
        self.VNA.write("CALC1:PAR3:FORM LOGPH")
        self.VNA.write("CALC1:PAR4:FORM LOGPH")

        self.VNA.write("DISP:WIND1:TRAC1:Y:AUTO")
        self.VNA.write("DISP:WIND1:TRAC2:Y:AUTO")
        self.VNA.write("DISP:WIND1:TRAC3:Y:AUTO")
        self.VNA.write("DISP:WIND1:TRAC4:Y:AUTO")

        self.VNA.timeout = 10000000

        self.VNA.write("SENS:SWE:POIN " + str(self.n_point))
        self.VNA.write("SENS:FREQ:START " + str(self.f_start))
        self.VNA.write("SENS:FREQ:STOP " + str(self.f_stop))
        self.VNA.write("SENS:BWID " + str(self.IFBW))
        # VNA.write("INIT:CONT ON;*OPC?")
        # VNA.read()
        # VNA.write("INIT:IMM;*OPC?")
        # VNA.read()
        # print("Pausing...")
        # time.sleep(5)
        #global t
        #t = VNA.query("SENS1:SWE:TIM?")
        self.VNA.write("SENS:HOLD:FUNC CONT")
        self.VNA.write("TRIG:SEQ:REM:SING")


    def getData(self):
        self.VNA.write("INIT:CONT OFF;*OPC?")
        self.VNA.read()
        freq = np.linspace(self.f_start, self.f_stop, self.n_point)

        self.VNA.write("FORM:DATA ASCii")

        # VNA.write("INIT:IMM;*OPC?")
        # VNA.read()
        # VNA.write("*WAI")

        self.VNA.write("SENS:HOLD:FUNC CONT")
        self.VNA.write("TRIG:SEQ:REM:SING")



        #print("Single Trigger Complete, *OPC? returned : " + VNA.query("INIT:IMM;*OPC?"))


        delete = (self.VNA.query("CALC1:DATA:FDAT?")[0:11])

        s11a = self.VNA.query("CALC1:DATA:FDAT?").replace(delete, '')
        self.VNA.write("CALC1:PAR2:SEL")
        s12a = self.VNA.query("CALC1:DATA:FDAT?").replace(delete, '')
        self.VNA.write("CALC1:PAR3:SEL")
        s21a = self.VNA.query("CALC1:DATA:FDAT?").replace(delete, '')
        self.VNA.write("CALC1:PAR4:SEL")
        s22a = self.VNA.query("CALC1:DATA:FDAT?").replace(delete, '')

        s11b = np.delete((np.array(s11a.split("\n"))), -1, 0)
        s21b = np.delete((np.array(s21a.split("\n"))), -1, 0)
        s12b = np.delete((np.array(s12a.split("\n"))), -1, 0)
        s22b = np.delete((np.array(s22a.split("\n"))), -1, 0)

        s11c = np.zeros((int(self.n_point), 2))
        s21c = np.zeros((int(self.n_point), 2))
        s12c = np.zeros((int(self.n_point), 2))
        s22c = np.zeros((int(self.n_point), 2))

        for m in range(int(self.n_point)):
            s11c[m] = s11b[m].split(",")
            s12c[m] = s12b[m].split(",")
            s21c[m] = s21b[m].split(",")
            s22c[m] = s22b[m].split(",")

            s11 = np.array(s11c).astype(float)
            s21 = np.array(s21c).astype(float)
            s12 = np.array(s12c).astype(float)
            s22 = np.array(s22c).astype(float)
            
        self.VNA.write("INIT:CONT ON")
            
        return s11, s12, s21, s22
        
        
        
if __name__ == '__main__':
    rm = visa.ResourceManager()
    print(rm.list_resources())