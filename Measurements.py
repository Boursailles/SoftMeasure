import numpy as np
from time import sleep, time
from statistics import mean 
import os
from SM.SM import COMMANDS as SM_COMMANDS, SETTINGS as SM_SETTINGS
from VNA.VNA import COMMANDS as VNA_COMMANDS, SETTINGS as VNA_SETTINGS



class SM(SM_SETTINGS, SM_COMMANDS):
    """SM measurement method used for SoftMeasure program.

    Args:
        SM_SETTINGS (obj): Settings of the SM.
        SM_COMMANDS (obj): Commands of the SM.
    """
    def __init__(self):
        """Initialize settings.
        """
        super().__init__()
    
    def connection(self, VNA=None):
        """Connection to the device.
        """
        # New parameters are saved.
        self.save_params()
        self.settings = {'device': str(self.device.currentIndex()), 'current': self.I.text(), 'measurement_period': self.meas_time.text()}
        
        # Connection to the device.
        SM_COMMANDS.__init__(self, self.settings)
        super().connection()
        self.led.turn_on()
        
        if VNA:
            self.record_method = 'record_with_VNA'
            self.step = VNA
            self.idx = 0
        else:
            self.record_method = 'record_without_VNA'
    
    def file(self, path):
        """Create measurement file

        Args:
            path (str): Directory path for recording files.
        """
        self.path = path
        
        # Creating iSHE voltage file.
        with open(os.path.join(self.path, 'V-iSHE_values.txt'), 'w') as f:
            f.write('iSHE Voltage [V]\n')

        # Creating iSHE delta (error) iSHE voltage file.
        with open(os.path.join(self.path, 'Delta_V-iSHE_values.txt'), 'w') as f:
            f.write('Detla iSHE Voltage [V]\n')
            
    def meas(self):
        """One measurement set with SM.
        """
        V_list = []
        start = now = time()

        # Set of SM measurement while a given time.
        while now - start < self.settings['time']:
            V = self.read_val()
            V_list.append(V)
            now = time()
                
        # Clear buffer.
        self.clear_buffer()
        
        # Averaging.
        V = mean(V_list)

        # Delta (error).
        sigma = max(abs(V - V_list))
        
        # Recording of values.
        getattr(self, self.record_method)(V, sigma)
          
    def record_with_VNA(self, V, sigma):
        """Measurement recording if VNA device is used.

        Args:
            V (float): Averaged voltage value.
            sigma (float): Error on voltage value.
        """
        # Recording of the averaged value.
        with open(os.path.join(self.path, 'V-iSHE_values.txt'), 'a') as f:
            f.write(str(V))
            # Voir comment arranger ça
            if self.idx < self.step - 1:
                f.write(', ')
            
        # Recording of the delta value.
        with open(os.path.join(self.path, 'Delta_V-iSHE_values.txt'), 'a') as f:
            f.write(str(sigma))
            # Voir comment arranger ça
            if self.idx < self.step - 1:
                f.write(', ')
                
    def record_without_VNA(self, V, sigma):
        """Measurement recording if VNA device is not used.

        Args:
            V (float): Averaged voltage value.
            sigma (float): Error on voltage value.
        """
        # Recording of the averaged value.
        with open(os.path.join(self.path, 'V-iSHE_values.txt'), 'a') as f:
            f.write(str(V))
            
        # Recording of the delta value.
        with open(os.path.join(self.path, 'Delta_V-iSHE_values.txt'), 'a') as f:
            f.write(str(sigma))
                  
    def off(self):
        """Set the device off.
        """
        super().off()
        self.led.turn_off()
            

class VNA(VNA_SETTINGS, VNA_COMMANDS):
    """VNA measurement method used for SoftMeasure program.

    Args:
        VNA_SETTINGS (obj): Settings of the VNA.
        VNA_COMMANDS (obj): Commands of the VNA.
    """
    def __init__(self):
        """Initialize settings.
        """
        super().__init__()
        
    def connection(self, SM=False):
        """Connection to the device.
        
        Args:
            SM (bool): Indicates if SM instrument is used or not. Default to False.
        """
        # New parameters are saved.
        self.save_params()
        self.settings = {'device': str(self.device.currentIndex()), 'f_start': self.f_start.text(), 'f_stop': self.f_stop.text(), 'nb_step': self.nb_step.text(), 'IFBW': self.IFBW.text(), 'power': str(self.power.currentIndex())}
        
        # Connection to the device.
        VNA_COMMANDS.__init__(self, self.settings)
        super().connection()
        self.led.turn_on()
        
        if SM:
            self.meas_method = 'meas_with_SM'
            # Iteration on the step number of the VNA.
            self.idx = 0
        else:
            self.meas_method = 'meas_without_SM'
            self.meas_settings(self.settings['nb_step'], self.settings['f_start'], self.settings['f_stop'])
            
        # Step number of the VNA.
        self.step = int(self.settings['nb_step'])
                        
    def file(self, path):
        """Create measurement file.

        Args:
            path (str): Directory path for recording files.
        """
        self.path = path

        # Creating frequency file with values.
        self.freq_list = np.linspace(float(self.settings['f_start']), float(self.settings['f_stop']), int(self.settings['nb_step']))
        np.savetxt(os.path.join(self.path, 'f_values.txt'), self.freq_list, header='Frequency [GHz]', comments='')
        
        # Creating S folder if it does not exist.
        self.s_path = os.path.join(self.path, 'S')
        try:
            os.makedirs(self.s_path)
        except FileExistsError:
            pass

        self.sij = ('S11', 'S12', 'S21', 'S22')
        for s in self.sij:
            # Creating Sij folders if they do not exist.
            path = os.path.join(self.s_path, s)
            try:
                os.makedirs(path)
            except FileExistsError:
                pass

            # Creating sij files.
            with open(os.path.join(path, 'Magnitude.txt'), 'w') as f:
                f.write(f'{s} Magnitude [dB]\n')
                
            with open(os.path.join(path, 'Phase.txt'), 'w') as f:
                    f.write(f'{s} Phase [rad]\n')
                    
    def meas(self):
        """Measurement with the initially chosen method (with or without SM).
        
        Args:
            idx (int): Index of the current applied current step of PS if the instrument is used (equal to 0 if not used).
        """
        getattr(self, self.meas_method)()
                    
    def meas_with_SM(self):
        """Measurement with VNA on one applied frequency.
        """
        freq = self.freq_list[self.idx]
        
        self.meas_settings('2', freq, freq + 1e-9)
        self.read_s_param()
        
        for s in self.sij:
            path = os.path.join(self.s_path, s)
            
            # Recording of the magnitude value.
            with open(os.path.join(path, 'Magnitude.txt'), 'a') as f:
                s_list = getattr(self.instr, s)['Magnitude']
                f.write(str(s_list[0]))
                
                if self.idx < self.step - 1:
                    f.write(', ')
            
            # Recording of the phase value.
            with open(os.path.join(path, 'Phase.txt'), 'a') as f:
                s_list = getattr(self.parent.vna.instr, s)['Phase']
                f.write(str(s_list[0]))
                
                if self.idx < self.step - 1:
                    f.write(', ')
        self.idx += 1
                    
    def meas_without_SM(self):
        """Measurement with VNA on a frequency sweep.
        """
        self.read_s_param()
        
        for s in self.sij:
            path = os.path.join(self.s_path, s)
            
            # Recording of the magnitude value.
            with open(os.path.join(path, 'Magnitude.txt'), 'a') as f:
                s_list = getattr(self.instr, s)['Magnitude']
                f.write(str(s_list[0]))
                
                for i, val in enumerate(s_list):
                    f.write(str(val))
                    if i < self.step - 1:
                        f.write(', ')
            
            # Recording of the phase value.
            with open(os.path.join(path, 'Phase.txt'), 'a') as f:
                s_list = getattr(self.parent.vna.instr, s)['Phase']
                f.write(str(s_list[0]))
                
                for i, val in enumerate(s_list):
                    f.write(str(val))
                    if i < self.step - 1:
                        f.write(', ')
    
    def off(self):
        """Set the device off.
        """
        self.led.turn_off()