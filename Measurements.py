from time import sleep, time
from statistics import mean 
import os
File_path = os.path.abspath(__file__)
Parent_path = os.path.dirname(File_path)
SM_path = os.path.join(Parent_path, 'SM')
from SM.SM import *


class SM(COMMANDS):
    """Measurement method used for SoftMeasure program.

    Args:
        COMMANDS (obj): Commands of the SM.
    """
    def __init__(self):
        """Initialize COMMANDS.
        """
        super().__init__()
        
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
            
