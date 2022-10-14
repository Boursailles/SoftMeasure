import pyvisa as visa
from PyQt5.QtWidgets import *
import numpy as np

#IMPORTANT: This code is not finished: See RS_ZNB_VNA as example and the pdf documentation for commands

###############################################################################
# This program is working with VNA_settings.py file for SoftMeasure.
# It contains useful code allowing to operate the Anritsu VNA, model ???
###############################################################################



class VNA:
    def __init__(self):
        """
        Anritsu VNA, model ???

        self.f_start: Starting frequency
        self.f_stop: Stopping frequency
        self.nb_point: Step number of frequencies
        self.IFBW: Intermediate Frequency Band Width
        self.power: Signal power
        """

        self.vna = None
        self.f_start = None
        self.f_stop = None
        self.nb_point = None
        self.IFBW = None
        self.power = None
        self.s11 =None
        self.s12 = None
        self.s21 = None
        self.s22 = None
        
        # Setup PyVISA instrument
        address_vna = "TCPIP0::169.254.239.174::INSTR"

        self.rm = visa.ResourceManager()
        try:
            self.vna = self.rm.open_resource(self.address_vna)
            print('Connected to ' + self.vna.query("*IDN?"))

        except visa.VisaIOError as e:
            QMessageBox.about(self, "Warning", "Connection issue with VNA\nError Codes: " + self.rm.last_status+"\t" + self.rm.visalib.last_status)



    def initialization(self, f_start, f_stop, nb_point, IFBW, power):
        """
        VNA initialization
        
        ---------
        Parameter:
        f_start: float
            Starting frequency
        f_stop: float
            Stopping frequency
        nb_point: int
            Step number
        IFBW: float
            Intermediate Frequency Band Width
        power: int
            Signal power
        """
        

        self.nb_point = nb_point
        self.f_start = f_start
        self.f_stop = f_stop
        self.IFBW = IFBW
        self.power = power

        # This command is working with Anritsu ? Try it
        #VNA.write("*RST")

        # If VNA takes more than 2 min to answer, something's wrong
        self.vna.timeout = 2 * 60 * 1e3

        # Define name trace with S parameter
        self.vna.write("CALC1:PAR1:FORM LOGPH")
        self.vna.write("CALC1:PAR2:FORM LOGPH")
        self.vna.write("CALC1:PAR3:FORM LOGPH")
        self.vna.write("CALC1:PAR4:FORM LOGPH")

        # Display 4 windows
        self.vna.write("DISP:WIND1:TRAC1:Y:AUTO")
        self.vna.write("DISP:WIND1:TRAC2:Y:AUTO")
        self.vna.write("DISP:WIND1:TRAC3:Y:AUTO")
        self.vna.write("DISP:WIND1:TRAC4:Y:AUTO")


        # Measure settings
        self.vna.write("SENS:SWE:POIN " + str(self.n_point))
        self.vna.write("SENS:FREQ:START " + str(self.f_start))
        self.vna.write("SENS:FREQ:STOP " + str(self.f_stop))
        self.vna.write("SENS:BWID " + str(self.IFBW))
        
        self.vna.write("SENS:HOLD:FUNC CONT")
        self.vna.write("TRIG:SEQ:REM:SING")


    def read_s_param(self):
        """
        Recording of S-parameters in the following dictionaries:
        self.instr.s11
        self.instr.s12
        self.instr.s21
        self.instr.s22

        Each are sorted like:
        self.instr.sij = {'dB': array, 'phase': array}
        """

        try:
            self.vna.write("INIT:CONT OFF;*OPC?")
            self.vna.read()

            self.vna.write("FORM:DATA ASCii")

            self.vna.write("SENS:HOLD:FUNC CONT")
            self.vna.write("TRIG:SEQ:REM:SING")


            delete = (self.vna.query("CALC1:DATA:FDAT?")[0:11])

            s11a = self.vna.query("CALC1:DATA:FDAT?").replace(delete, '')
            self.vna.write("CALC1:PAR2:SEL")
            s12a = self.vna.query("CALC1:DATA:FDAT?").replace(delete, '')
            self.vna.write("CALC1:PAR3:SEL")
            s21a = self.vna.query("CALC1:DATA:FDAT?").replace(delete, '')
            self.vna.write("CALC1:PAR4:SEL")
            s22a = self.vna.query("CALC1:DATA:FDAT?").replace(delete, '')

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
                
            self.vna.write("INIT:CONT ON")


        except visa.VisaIOError as e:
            QMessageBox.about(self, "Warning", "Connection issue with VNA\nError Codes: " + self.rm.last_status+"\t" + self.rm.visalib.last_status)