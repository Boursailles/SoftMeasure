import numpy as np
from time import sleep, time
from statistics import mean 
import os
from SM.SM import COMMANDS as SM_COMMANDS
from SM.SM import SETTINGS as SM_SETTINGS
from VNA.VNA import COMMANDS as VNA_COMMANDS
from VNA.VNA import SETTINGS as VNA_SETTINGS



class SM(SM_SETTINGS, SM_COMMANDS):
    """Measurement method used for SoftMeasure program.

    Args:
        SM_SETTINGS (obj): Settings of the SM.
        SM_COMMANDS (obj): Commands of the SM.
    """
    def __init__(self):
        """Initialize settings.
        """
        super().__init__()
    
    def connection(self):
        """Connection to the device.
        """
        self.settings = {'device': self.device.text(), 'current': self.I.text(), 'measurement_period': self.meas_time.text()}
        SM_COMMANDS.__init__(self, self.settings)
        super().connection()
    
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

    
        # Recording of the averaged value.
        with open(os.path.join(self.path, 'V-iSHE_values.txt'), 'a') as f:
            f.write(str(V))
            # Voir comment arranger ça
            """if self.parent.vna.box.isChecked() and idx < len_loop-1:
                f.write(', ')"""
            
        # Recording of the delta value.
        with open(os.path.join(self.path, 'Delta_V-iSHE_values.txt'), 'a') as f:
            f.write(str(sigma))
            # Voir comment arranger ça
            """
            if self.parent.vna.box.isChecked() and idx < len_loop-1:
                f.write(', ')"""
            

class VNA(VNA_SETTINGS, VNA_COMMANDS):
    """Measurement method used for SoftMeasure program.

    Args:
        VNA_COMMANDS (obj): Commands of the VNA.
    """
    def __init__(self, SM=False, PS=0):
        """Initialize settings.
        
        Args:
            SM (bool): Indicates if SM instrument is used or not. Default to False.
            PS (any): If PS instrument is used, give its number of iterations. Default to 0.
        """
        if SM:
            self.meas_method = 'meas_with_SM'
            # Iteration on the step number of the VNA.
            self.idx = 0
        else:
            self.meas_method = 'meas_without_SM'
            
        # Step number of the VNA.
        self.step = int(self.settings['nb_step'])
            
        if not PS:
            self.nb_iterations = 0
            
        super().__init__()
        
        
    def connection(self):
        """Connection to the device.
        """
        self.settings = {'device': self.device.text(), 'IFBW': self.IFBW.text(), 'power': self.power.text(), 'f_start': self.f_start.text(), 'f_stop': self.f_stop.text(), 'nb_step': self.nb_step.text()}
        
        
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
        getattr(self, self.meas_method)
        
        # Recording in files VNA measurements.
        self.record(idx)
                    
    def meas_with_SM(self):
        """One Measurement with VNA on one applied frequency.
        """
        freq = self.freq_list[self.idx]
        self.idx += 1
        
        self.meas_settings('2', freq, freq + 1e-9)
        self.read_s_param()
        
        for s in self.sij:
            path = os.path.join(self.s_path, s)
            
            # Recording of the magnitude value.
            with open(os.path.join(path, 'Magnitude.txt'), 'a') as f:
                s_list = getattr(self.instr, s)['Magnitude']
                f.write(str(s_list[0]))
                
                if idx < self.nb_iterations - 1:
                    f.write(', ')
                    
    def meas_without_SM(self):
        self.meas_settings(self.settings['nb_step'], self.settings['f_start'], self.settings['f_stop'])
        self.read_s_param()
        
    def record(self, idx):
        """Recording of S-parameters.

        Args:
            idx (int): Index of the current applied current step of PS if the instrument is used (equal to 0 if not used).
        """
        for s in self.sij:
            path = os.path.join(self.s_path, s)
            
            # Recording of the magnitude value.
            with open(os.path.join(path, 'Magnitude.txt'), 'a') as f:
                s_list = getattr(self.instr, s)['Magnitude']
                f.write(str(s_list[0]))
                
                if idx < self.nb_iterations - 1:
                    f.write(', ')
                
                else:
                    s_len = len(s_list)
                    for i, val in enumerate(s_list):
                        f.write(str(val))
                        if i < s_len - 1:
                            f.write(', ')
            
            # Recording of the phase value.
            with open(os.path.join(path, 'Phase.txt'), 'a') as f:
                s_list = getattr(self.parent.vna.instr, s)['Phase']
                f.write(str(s_list[0]))
                
                if idx < self.nb_iterations - 1:
                    f.write(', ')
                
                else:
                    s_len = len(s_list)
                    for i, val in enumerate(s_list):
                        f.write(str(val))
                        if i < s_len - 1:
                            f.write(', ')
    