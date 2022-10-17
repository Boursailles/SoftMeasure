from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import os
import pyvisa as visa
import numpy as np



class Measures:
    def __init__(self, vna, ps, gm, path):

        # Creating folder from path if it did not exist.
        try:
            os.makedirs(s)
        except FileExistsError:
            pass


        if vna:
            # Creating S and Sij folders if they did not exist.
            s_path = os.path.join(path, 'S')
            try:
                os.makedirs(s_path)
            except FileExistsError:
                pass
                
            sij = ('S11', 'S12', 'S21', 'S22')
            for s in sij:
                try:
                    os.makedirs(os.path.join(s_path, s))
                except FileExistsError:
                    continue
        

        if ps:
            # Creating S and Sij folders if they did not exist.
            s_path = os.path.join(path, 'S')
            try:
                os.makedirs(s_path)
            except FileExistsError:
                pass
