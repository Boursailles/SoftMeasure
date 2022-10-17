import pyvisa
import math
from time import sleep
#from serial.tools import list_ports
import numpy as np

#ports = [port.name for port in list_ports.comports()]


class Danfysik9700VISADriver:
    """
        VISA class driver for the Danfysik 9700 Magnet Power Source
        This class relies on pyvisa module to communicate with the instrument via VISA protocol
        Please refer to the instrument reference manual available at:
    """

    units = 'A'

    def __init__(self):
        super().__init__()
        self._instr=None
        #self._VISA_rm = pyvisa.ResourceManager.open_resource('ASRL3::INSTR') #.open_resource('ASRL3::INSTR')
        #self.com_ports = self.get_ressources()

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

    # def get_ressources(self):
    #     infos=self._VISA_rm.list_resources_info()
    #     com_ports=[infos[key].alias for key in infos.keys()]
    #     return com_ports

    def get_identification(self):
        self._instr.write("PRINT")
        id = self._instr.read()
        self._instr.read()
        sleep(0.005)
        return id
 
    def get_polarity(self):
        """ The polarity of the current supply, being either
        -1 or 1.
        """
        value = None
        self._instr.write("PO")
        sleep(0.05)
        value = self._instr.read()
        return 1 if value == '+' else -1

    def set_polarity(self, polarity):
        """ Set the polarity of the current supply.
        """
        assert (isinstance(polarity, str))
        value = polarity.lower()

        cmd = 'PO '

        if value == "POSITIVE".lower():
            cmd += "+"
        elif value == "NEGATIVE".lower():
            cmd += "-"

        self._instr.write(cmd)

    def read_current(self):
        """ 
        The actual current in Amps.
        """
        val1 = None
        self._instr.write("AD 8")
        sleep(0.05)
        val1 = self._instr.read()
        val2 = int(val1)*0.01

        return val2 #do not forget to check polarity in the main !!!


    def set_current(self, amps):
        """Set the current in Amps. This property is set through
        :attr:`~.current_ppm`."""
        self.current_ppm = int((1e6/1000)*amps)

    @property
    def current_ppm(self):
        """
        The current in parts per million. This property can be set.
        """
        self._instr.write("DA 0")
        val = self._instr.read()
        return int(val)

    @current_ppm.setter
    def current_ppm(self, ppm):
        """
        Setting the current in parts per million
        """
        self._instr.write("DA 0,%d" % ppm)
    
    @property
    def current_setpoint(self):
        """ The setpoint for the current, which can deviate from the actual current
        (:attr:`~.Danfysik9100.current`) while the supply is in the process of setting the value.
        """
        return self.current_ppm*(1000/1e6)

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



class DanWithTau(Danfysik9700VISADriver):

    units = 'A'

    def __init__(self):
        super().__init__()
        self._instr = None
        self._epsilon = 1e-3
        self._tau = 200
        self.I_global = 0
        
        self.init_communication()
        self.unlock()
        self.remote()
        self.enable()


    @property
    def epsilon(self):
        return self._epsilon

    @epsilon.setter
    def epsilon(self, eps):
        self._epsilon = eps

    @property
    def tau(self):
        """
        fetch the characteristic decay time in s
        Returns
        -------
        float: the current characteristic decay time value
        """
        return self._tau

    @tau.setter
    def tau(self, value):
        """
        Set the characteristic decay time value in s
        Parameters
        ----------
        value: (float) a strictly positive characteristic decay time
        """
        if value <= 0:
            raise ValueError(f'A characteristic decay time of {value} is not possible. You must be positive')
        else:
            self._tau = value

    
    def set_current(self, amps):
        """Set the current in Amps in an exponential decay. This property is set through
        :attr:`~.current_ppm`."""
        polar = self.get_polarity()
        I_start_temp = abs(self.read_I_temp())
        I_start = I_start_temp*polar
        I_temp= float(50)
        I_stop = amps
        I_read = abs(self.read_current())
        I_start_read = I_read*polar

        if abs(I_start_read)-abs(I_start) > 0.05:
            I_start = I_start_read
        else:
            pass

        i = 0

        if I_stop == 0:
            I_stop = polar*0.001
        else:
            pass

        if abs(I_start-I_stop) <= 0.001:
            self.current_ppm = int((1e6 / 1000) * I_stop)
            sleep(0.008)
            I_temp = I_stop

        elif self.epsilon + 0.001 >= abs(I_stop-I_start) > 0.001 :
            while abs(I_temp - I_stop) > 0.0001 or I_temp != I_stop:
                i = i + 1
                I_temp = I_start + np.sign(I_stop - I_start) * i * 0.001
                self.current_ppm = int((1e6 / 1000) * I_temp)
                sleep(0.008)

        else:
            delta_I = I_stop - I_start
            I_temp = I_start
            while abs(I_temp - I_stop) > self.epsilon:
                i = i + 1
                I_temp = I_temp + delta_I/2
                delta_I = I_stop - I_temp
                self.current_ppm = int((1e6 / 1000) * I_temp)
                sleep(0.5)


            
        self.I_global = I_temp



    def set_current_normal(self, amps):
        """Set the current in Amps. This property is set through
        :attr:`~.current_ppm`."""
        self.current_ppm = int((1e6 / 1000) * amps)
        if amps == 0:
            self.I_global = 0
        else:
            pass
        
        
        
    def set(self, position):
        """
        Move the actuator to the absolute target defined by position

        Parameters
        ----------
        position: (float) value of the absolute target positioning
        """
        polar = self.get_polarity()
        


        """CHANGE LE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"""
        #position = self.check_bound(position)  # limits the position within the specified bounds (-38,38)

        if position == 0:
            self.set_current(0.001)
            self.set_current_normal(0)
            #self.move_done_I_set()
            #self.move_done()

        elif np.sign(position) == np.sign(polar):

            ## OK TODO for your custom plugin
            self.set_current(position)
            ##############################

            self.target_position = position
            #self.move_done_I_set()
            #self.move_done()
            # self.poll_moving() # start a loop to poll the current actuator value and compare it with target position

        else:
            self.set_current(0.001)
            self.set_current_normal(0)
            self.target_position = 0

            # sleep(0.01)

            if np.sign(polar) > 0:
                self.set_polarity("NEGATIVE")
            else:
                self.set_polarity("POSITIVE")

            # sleep(0.1)
            self.set_current(position)
            self.target_position = position
            #self.move_done_I_set()
            #self.move_done()
                # self.poll_moving()



    def truncate2(self, value):
        precision = 2
        x = 10.0 ** precision
        num = int(value * x) / x
        return num



    def truncate3(self, value):
        precision = 3
        x = 10.0 ** precision
        num = int(value * x) / x
        return num



    def truncate4(self, value):
        precision = 4
        x = 10.0 ** precision
        num = int(value * x) / x
        return num



    def read_I_temp(self):
        polar = self.get_polarity()
        if 0 <= abs(self.I_global) < 1:
            return self.truncate4(self.I_global)*polar
        elif 1 <= abs(self.I_global) < 10:
            return self.truncate3(self.I_global)*polar
        else:
            return self.truncate2(self.I_global)*polar
        
    
    def off(self):
        self.set(0)
        self.disable()
        self.local()
        self.close_communication()




if __name__ == "__main__":
    try:
        D9700 = DanWithTau()
        D9700.off()

    except Exception as e:
        print("Exception ({}): {}".format(type(e), str(e)))

