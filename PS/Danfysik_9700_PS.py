import pyvisa as visa
from PyQt5.QtWidgets import *
from time import sleep



###############################################################################
# This program is working with PS_settings.py file for SoftMeasure.
# It contains useful code allowing to operate the Danfysik Power Supply (PS), model 9700.
###############################################################################



class PS:
    def __init__(self, rm):
        """
        Danfysik PS, model 9700

        self.I_start: Starting current
        self.f_stop: Stopping current
        self.nb_step: Step number of current values
        """

        self.ps = None
        self.I_start = None
        self.I_stop = None
        self.nb_step = None
        self.epsilon = 4e-4

        # Setup PyVISA instrument
        self.address_ps = 'ASRL1::INSTR'

        rm = visa.ResourceManager()
        self.ps = rm.open_resource(self.address_ps)
        print('Connected to ' + self.ps.query("*IDN?"))

        # set attributes
        self.ps.baud_rate = 115200
        self.ps.data_bits = 8
        self.ps.stop_bits = visa.constants.StopBits['one']
        self.ps.parity = visa.constants.Parity['none']
        self.ps.read_termination = '\n\r'
        self.ps.write_termination = '\r'

    
    def initialization(self):
        """
        PS initialization
        """

        self.unlock()
        self.remote()
        self.enable()

        self._current_ppm = 0
        self.set_amps(0)


    def set_current(self, amps):
        """
        Sets the current in Amps by dichotomy.
        """

        I_start = self.current_ppm*1e-3
        I_temp = I_start
        I_stop = amps        

        delta_I = I_stop - I_start
        while abs(delta_I) > self.epsilon:
            I_temp += delta_I/2
            delta_I = I_stop - I_temp
            self.set_current(I_temp)
            sleep(0.5)

        self.set_current(I_stop)
        
        
    def set_amps(self, amps):
        """
        Set the current in Amps. This property is set through :attr:`~.current_ppm`.
        """

        self.current_ppm = int((1e6/1000)*amps)


    @property
    def current_ppm(self):
        """
        The current in parts per million.
        """
        
        return int(self._current_ppm)

    @current_ppm.setter
    def current_ppm(self, ppm):
        """
        Setting the current in parts per million.
        """

        self._current_ppm = ppm
        self.ps.write("DA 0,%d" % ppm)


    def off(self):
        """
        Closes communication.
        """
        self.set_current(0)
        self.disable()
        self.local()
        self.ps.close()


    def unlock(self):
        self.ps.write("UNLOCK")


    def remote(self):
        """
        Sets the PS in remote mode where the front panel is disabled.
        """

        self.ps.write("REM")


    def local(self):
        """
        Sets the PS in local mode, where the front panel can be used.
        """

        self.ps.write("LOC")


    def enable(self):
        """
        Enables the flow of current.
        """
        self.ps.write("N")


    def disable(self):
        """
        Disables the flow of current.
        """

        self.ps.write("F")



if __name__ == '__main__':
    try:
        D9700 = PS()
        D9700.off()
    except Exception as e:
        print("Exception ({}): {}".format(type(e), str(e)))


