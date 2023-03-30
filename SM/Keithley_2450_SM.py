import pyvisa as visa



###############################################################################
# This program is working with SM_settings.py file for SoftMeasure.
# It contains useful code allowing to operate the Keithley SourceMeter (SM), model 2450.
###############################################################################



class SM(object):
    def __init__(self):
        """
        Keithley LS, model 2450
        """

        rm = visa.ResourceManager()
        self.sm = None

        # Setup PyVISA instrument
        self.address_sm = 'USB0::0x05E6::0x2450::04096941::INSTR'

        self.sm = rm.open_resource(self.address_sm)
        print('Connected to ' + self.sm.query("*IDN?"))


    def initialization(self, I):
        """
        SM initialization

        ---------
        Parameter:
        I: str
            Applied current in the SM
        """

        # If SM takes more than 2 min to answer, something's wrong
        self.sm.timeout = 2 * 60 * 1e3

        # Reset instrument
        #self.sm.write('*RST')
        # The instrument with working as a current sourcing
        self.sm.write('SOUR:FUNC CURR')
        # Value of the applied current
        self.sm.write('SOUR:CURR:RANG ' + I)
        self.sm.write('SOUR:CURR ' + I)
        # Applying of the current
        self.sm.write('OUTP ON')

        """self.sm.write('VOLT:AVER:COUNT 10')
        self.sm.write('VOLT:AVER:TCON REP')
        self.sm.write('VOLT:AVER ON')"""


    def read_val(self):
        """
        Recording of voltage value.
        """

        # Make measurement
        self.sm.query('MEAS:VOLT?')

        # Take index of last measurement
        idx = int(self.sm.query(':TRAC:ACT:END?'))
        V = self.sm.query(f'TRAC:DATA? {idx}, {idx}')
        V = float(V.replace('\n', ''))
        return V
        
        
    def clear_buffer(self):
        """
        Clear active buffer.
        """
        self.sm.write('TRAC:CLE "defbuffer1"')
        
        

    
    def off(self):
        self.sm.write('OUTP OFF')
        #self.sm.write('*RST')
        
        

        
        

if __name__ == '__main__':
    import pyvisa as visa

    rm = visa.ResourceManager()