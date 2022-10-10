import pyvisa as visa
import numpy as np
import datetime

class RSZNB40VNA:
    def __init__(self, n_point, f_start, f_stop, IFBW):
        """
        Rhode-Schwarz VNA, model ZNB40
        :param IFBW: bandwidth in kHz
        """
        self.n_point = n_point
        self.f_start = f_start
        self.f_stop = f_stop
        self.IFBW = IFBW

        # Setup PyVISA instrument
        address_vna = "TCPIP0::ZNB40-72-101845::inst0::INSTR"
        # https://stackoverflow.com/a/39066537
        self.rm = visa.ResourceManager()
        try:
            self.vna = self.rm.open_resource(address_vna)
        except visa.VisaIOError as e:
            print(e.args)
            print(self.rm.last_status)
            print(self.rm.visalib.last_status)
        print('Connected to '+ self.vna.query("*IDN?"))

        self.vna.write("*RST")
        
        # Timeout in ms: https://pyvisa.readthedocs.io/en/1.8/resources.html#timeout
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
        self.vna.write("SWE:POIN " + str(self.n_point))
        self.vna.write("FREQ:STAR " + str(self.f_start))
        self.vna.write("FREQ:STOP " + str(self.f_stop))
        self.vna.write("BWID " + str(self.IFBW))

        self.vna.write("INIT:CONT:ALL ON; *WAI")
        self.vna.write("SOUR:POW -10")

    def read_s_param(self):
        print('Started S param queries at %s' % str(datetime.datetime.now()))
        s11, s12, s21, s22 = None, None, None, None

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
            
            print('Finished S param queries at %s' % str(datetime.datetime.now()))
        
        except visa.VisaIOError as e:
            # https://stackoverflow.com/a/39066537
            print("Error in RSZNB40VNA.read_s_param()")
            print(e.args)
            print(self.rm.last_status)
            print(self.rm.visalib.last_status)
      
        return s11, s12, s21, s22
        
        
        
if __name__ == '__main__':
    n_point = 3001
    f_start = 100.0e6
    f_stop = 20.0e9
    IFBW = 1e3
    
    test = RSZNB40VNA(n_point, f_start, f_stop, IFBW)
    s11, s12, s21, s22 = test.read_s_param()
    print(s11)