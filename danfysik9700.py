from importlib.machinery import FileFinder
from shutil import _ntuple_diskusage
from zoneinfo import ZoneInfoNotFoundError
import pyvisa
import math
from time import sleep
#from serial.tools import list_ports
import numpy as np

#ports = [port.name for port in list_ports.comports()]


class danfysik9700:

    units = 'A'


    """
        VISA class driver for the Kikusui PBZ60 Power Source
        This class relies on pyvisa module to communicate with the instrument via VISA protocol
    """
    def __init__(self):
        super().__init__()
        #self._com_port = ''
        self._instr = None
        self.epsilon = 4e-4
        self.wait = 5
        self.coeff = 2


        self.init_communication()
        self.unlock()
        self.remote()
        self.enable()

        # keep track of the active current
        self._current_ppm = 0
        self.set_current(0)
    

    def init_communication(self):

        rm = pyvisa.ResourceManager()
        self._instr = rm.open_resource('ASRL1::INSTR')
        
        # set attributes
        self._instr.baud_rate = 115200
        self._instr.data_bits = 8
        self._instr.stop_bits = pyvisa.constants.StopBits['one']
        self._instr.parity = pyvisa.constants.Parity['none']
        self._instr.read_termination = '\n\r'
        self._instr.write_termination = '\r'

        print('Connected to ' + self._instr.query("*IDN?"))

            
    def close_communication(self):
        self._instr.write("F")
        self._instr.close()
        #self._VISA_rm.close()
        
    def _query(self, command):
        ret = self._instr.query(command)
        return ret

    def _write_command(self, command):
        self._instr.write(command)

    def get_identification(self):
        self._instr.write("PRINT")
        id = self._instr.read()
        self._instr.read()
        sleep(0.005)
        return id
    
    def enable(self):
        """ Enables the flow of current.
        """
        self._instr.write("N")

    def disable(self):
        """ Disables the flow of current.
        """
        self._instr.write("F")

    def local(self):
        """ Sets the instrument in local mode, where the front
        panel can be used.
        """
        self._instr.write("LOC")

    def remote(self):
        """ Sets the instrument in remote mode, where the front
        panel is disabled.
        """
        self._instr.write("REM")

    def unlock(self):
        self._instr.write("UNLOCK")

    def initialize(self):
        #self._instr.write("UNLOCK")
        #sleep(0.01)
        self._instr.write("REM")
        sleep(0.01)
        self._instr.write("N")
        sleep(0.01)


    def set_current(self, amps):
        """Set the current in Amps. This property is set through
        :attr:`~.current_ppm`."""
        self.current_ppm = int((1e6/1000)*amps)

    @property
    def current_ppm(self):
        """
        The current in parts per million. This property can be set.
        """
        '''self._instr.write("DA 7")
        val = self._instr.read()
        print("RAW answer: %s" % str(val))
        val = val[2:]'''
        return int(self._current_ppm)

    @current_ppm.setter
    def current_ppm(self, ppm):
        """
        Setting the current in parts per million
        """
        self._current_ppm = ppm
        print("PPM = %d" % ppm)
        self._instr.write("DA 0,%d" % ppm)


    def set(self, amps):
        """Set the current in Amps in an exponential decay. This property is set through
        :attr:`~.current_ppm`."""
        '''
        Iread = self.current_ppm
        I_start = float(Iread)*1e-3
        print("Current current: %0.3f A" % I_start)
        print(I_start)'''

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


    def off(self):
        self.set(0)
        self.disable()
        self.local()
        self.close_communication()


if __name__ == '__main__':
    try:
        D9700 = danfysik9700()
        D9700.off()
    except Exception as e:
        print("Exception ({}): {}".format(type(e), str(e)))


