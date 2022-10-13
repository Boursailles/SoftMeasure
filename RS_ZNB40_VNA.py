import pyvisa as visa
from PyQt5.QtWidgets import *
import numpy as np



###############################################################################
# This program is working with VNA_settings.py file for SoftMeasure.
# It contains useful code allowing to operate the Rhode-Schwarz VNA, model ZNB40
###############################################################################



class VNA:
    def __init__(self):
        """
        Rhode-Schwarz VNA, model ZNB40

        self.f_start: Starting frequency
        self.f_stop: Stopping frequency
        self.nb_point: Step number of frequencies
        self.IFBW: Intermediate Frequency Band Width
        self.power: Signal power
        """

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
        self.address_vna = "TCPIP0::ZNB40-72-101845::inst0::INSTR"
        # https://stackoverflow.com/a/39066537
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


        self.vna.write("*RST")

        # If VNA takes more than 2 min to answer, something's wrong
        # TODO: compute this from the sweep time
        self.vna.timeout = 2 * 60 * 1e3

        # Define name trace with S parameter
        self.vna.write("CALC:PAR:SDEF 'Trc1', 'S11'")
        self.vna.write("CALC:PAR:SDEF 'Trc2', 'S12'")
        self.vna.write("CALC:PAR:SDEF 'Trc3', 'S21'")
        self.vna.write("CALC:PAR:SDEF 'Trc4', 'S22'")
        
        self.vna.write("CALC:PAR:SDEF 'Trc5', 'S11'")
        self.vna.write("CALC:FORM PHAS")
        self.vna.write("CALC:PAR:SDEF 'Trc6', 'S12'")
        self.vna.write("CALC:FORM PHAS")
        self.vna.write("CALC:PAR:SDEF 'Trc7', 'S21'")
        self.vna.write("CALC:FORM PHAS")
        self.vna.write("CALC:PAR:SDEF 'Trc8', 'S22'")
        self.vna.write("CALC:FORM PHAS")
        
        
        # Display 4 windows
        self.vna.write("DISP:WIND1:STAT ON")
        self.vna.write("DISP:WIND2:STAT ON")
        self.vna.write("DISP:WIND3:STAT ON")
        self.vna.write("DISP:WIND4:STAT ON")
        
        self.vna.write("DISP:WIND5:STAT ON")
        self.vna.write("DISP:WIND6:STAT ON")
        self.vna.write("DISP:WIND7:STAT ON")
        self.vna.write("DISP:WIND8:STAT ON")
        
        
        # Display each trace to each window
        self.vna.write("DISP:WIND1:TRAC:FEED 'Trc1'")
        self.vna.write("DISP:WIND2:TRAC:FEED 'Trc2'")
        self.vna.write("DISP:WIND3:TRAC:FEED 'Trc3'")
        self.vna.write("DISP:WIND4:TRAC:FEED 'Trc4'")
        
        self.vna.write("DISP:WIND5:TRAC:FEED 'Trc5'")
        self.vna.write("DISP:WIND6:TRAC:FEED 'Trc6'")
        self.vna.write("DISP:WIND7:TRAC:FEED 'Trc7'")
        self.vna.write("DISP:WIND8:TRAC:FEED 'Trc8'")
        
        
        # Auto-scale Y-axis
        self.vna.write("DISP:TRAC:Y:AUTO ONCE, 'Trc1'")
        self.vna.write("DISP:TRAC:Y:AUTO ONCE, 'Trc2'")
        self.vna.write("DISP:TRAC:Y:AUTO ONCE, 'Trc3'")
        self.vna.write("DISP:TRAC:Y:AUTO ONCE, 'Trc4'")

        self.vna.write("DISP:TRAC:Y:AUTO ONCE, 'Trc5'")
        self.vna.write("DISP:TRAC:Y:AUTO ONCE, 'Trc6'")
        self.vna.write("DISP:TRAC:Y:AUTO ONCE, 'Trc7'")
        self.vna.write("DISP:TRAC:Y:AUTO ONCE, 'Trc8'")
        
        
        # Measure settings
        self.vna.write("SWE:POIN " + str(self.nb_point))
        self.vna.write("FREQ:STAR " + str(self.f_start))
        self.vna.write("FREQ:STOP " + str(self.f_stop))
        self.vna.write("BWID " + str(self.IFBW))

        self.vna.write("INIT:CONT:ALL ON; *WAI")
        self.vna.write("SOUR:POW " + str(self.power))


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
            self.vna.write("INIT:CONT OFF; :INIT; *WAI")

            self.vna.write("INIT:CONT:ALL ON")
            
            self.vna.write("DISP:TRAC1:Y:AUTO ONCE, 'Trc1'")
            self.vna.write("DISP:TRAC2:Y:AUTO ONCE, 'Trc2'")
            self.vna.write("DISP:TRAC3:Y:AUTO ONCE, 'Trc3'")
            self.vna.write("DISP:TRAC4:Y:AUTO ONCE, 'Trc4'")
                    

            self.vna.write("FORM:DATA ASCii")

            s11_dB = self.vna.query("CALC:DATA:TRAC? 'Trc1', FDAT")[:-1]
            s11_phase = self.vna.query("CALC:DATA:TRAC? 'Trc5', FDAT")[:-1]
            
            s12_dB = self.vna.query("CALC:DATA:TRAC? 'Trc2', FDAT")[:-1]
            s12_phase = self.vna.query("CALC:DATA:TRAC? 'Trc6', FDAT")[:-1]
            
            s21_dB = self.vna.query("CALC:DATA:TRAC? 'Trc3', FDAT")[:-1]
            s21_phase = self.vna.query("CALC:DATA:TRAC? 'Trc7', FDAT")[:-1]
            
            s22_dB = self.vna.query("CALC:DATA:TRAC? 'Trc4', FDAT")[:-1]
            s22_phase = self.vna.query("CALC:DATA:TRAC? 'Trc8', FDAT")[:-1]
            
            
            s11_dB = np.array([float(val) for val in s11_dB.split(',')])
            s11_phase = np.array([float(val) for val in s11_phase.split(',')])
            
            s12_dB = np.array([float(val) for val in s12_dB.split(',')])
            s12_phase = np.array([float(val) for val in s12_phase.split(',')])
            
            s21_dB = np.array([float(val) for val in s21_dB.split(',')])
            s21_phase = np.array([float(val) for val in s21_phase.split(',')])
            
            s22_dB = np.array([float(val) for val in s22_dB.split(',')])
            s22_phase = np.array([float(val) for val in s22_phase.split(',')])
            

            self.s11 = {'dB': s11_dB, 'phase': s11_phase}
            self.s12 = {'dB': s12_dB, 'phase': s12_phase}
            self.s21 = {'dB': s21_dB, 'phase': s21_phase}
            self.s22 = {'dB': s22_dB, 'phase': s22_phase}


        except visa.VisaIOError as e:
            QMessageBox.about(self, "Warning", "Connection issue with VNA\nError Codes: " + self.rm.last_status+"\t" + self.rm.visalib.last_status)
