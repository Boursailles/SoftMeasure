###############################################################################
# This program is working with SM_settings.py file for SoftMeasure.
# It contains useful code allowing to operate the Keithley SourceMeter (SM), model 2450.
###############################################################################



class SM(object):
    def __init__(self, rm):
        """
        Keithley LS, model 2450

        self.V: iSHE voltage
        ---------
        Parameter:
        rm: class
            Ressource Manager
        """

        self.sm = None
        self.V = None

        # Setup PyVISA instrument
        self.address_gm = 'SM_address'

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

        # Reset instrument
        self.sm.write('*RST')
        # The instrument with working as a current sourcing
        self.sm.write('SOUR:FUNC:CURR')
        # Value of the applied current
        self.sm.write('SOUR:CURR:RANG ' + I)
        # Applying of the current
        self.sm.write('OUTP ON')


    def read_val(self):
        """
        Recording of voltage value
        """

        self.V = self.sm.write('MEAS:VOLT?')

    
    def off(self):
        self.sm.write('OUTP OFF')
        self.sm.wrte('*RST')

        
        

if __name__ == '__main__':
    import pyvisa as visa

    rm = visa.ResourceManager()
    
    test = SM(rm)
    test.initialization('1e-8')
    test.read_val()
    test.off()

    print(test.V)