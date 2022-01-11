from inspect import modulesbyfile
import numpy as np
import matplotlib.pyplot as plt
import csv
import pandas as pd 
import scipy.optimize as scp
import warnings




#***************************************************************************************************************#
# This program is working with Interface.py file for SoftMeasure.
# It contains physics models of the photon-magnon hybridization and fit functions
#***************************************************************************************************************#




class models(object):
    # Contains physics models of the photon-magnon hybridization and fit functions
    def __init__(self):
        self.freq_c =None
        
        self.len_x = 3001
        self.len_y = 1401
        self.S_max = -35
        self.S_min = -100
        
    

    def lorentzian(self, x, x0):
        # Lorentzian equation which permits to imitate S21 parameter
        return 1/(1 + 4*(x - x0)**2/0.01)
    
    
    
    def search_freq_c(self, freq, S21):
        # Method taking freq values and 2 columns array, each being S21 values for H=max and H=0
        # Return the frequence of the cavity
        S21_first = S21[0]
        S21_last = S21[1]
        
        
        def covid(freq, S21):
            # Function returning the frequence of the cavity
            # Using the covariance of the S21(freq) curve with a Lorentzian
            # Permits to exhibit DM and BM modes with reducing the noise
            
            self.S21_min = min(S21)
            self.S21_max = max(S21)
        
            S21 = np.maximum(S21, np.mean(S21)) - np.mean(S21)
            
            
            cov = np.zeros_like(freq)
            counter = 0
            for i in range(2, len(freq)):
                lolo = self.lorentzian(freq, freq[i])*abs(self.S21_max - self.S21_min)
                cov[i] = np.cov(S21, lolo)[0, 1]
                if cov[i-2] < cov[i-1] > cov[i] and\
                    (abs(cov[i-1] - cov[i-2]) > 4e-4 or abs(cov[i-1] - cov[i]) > 4e-4):
                    # Detection of a mode
                    if counter == 0:
                        # This is a DM mode, we don't care about it
                        counter += 1
                    else:
                        # This is a BM mode, the frequency of the cavity which interests us
                        return freq[i-1]
                    
        freq_c_first = covid(freq, S21_first)
        freq_c_last = covid(freq, S21_last)
        
        # Average of the two BM modes found out for each H values
        self.freq_c = (freq_c_first + freq_c_last)/2
        
    
        
    def slab_model_3D(self, pos, g):
        # Rectangular prism model
        # Take a 2D list of all freq and H associated values (pos), and the strentgh coupling (g)
        # Example for pos: [[1, 1, 1, 2, 2, 2], [0, 0.1, 0.2, 0, 0.1, 0.2]]\
        # for 2 freq points equal to 1 and 2 and 3 H points equal to 0.1, 0.2, and 0.3
        # Return the artificial S21 parameters for each f and H values in 1D array
        
        # Prism dimensions
        a = 0.25
        b = 3
        c = 2
        
        # Ferrimagnetic parameters (default: YIG)
        Ms = 0.176
        gamma = 28
        
        
        np.seterr(all='warn')
        warnings.filterwarnings('error')
                
                
        def f_func(x, y, z):
            # Function from the rectangular prism model
            return (np.sqrt(x*x + y*y + z*z)*z)/(x*y)
            
        # Diagonal components of the demagnetizing tensor
        Nzz = 2/(np.pi)*np.arctan(1/f_func(a, b, c))
        Nxx = 2/(np.pi)*np.arctan(1/f_func(c, b, a))
        Nyy = 2/(np.pi)*np.arctan(1/f_func(a, c, b))
                
                
        def G_func(x, y, z):
            # Function from the rectangular prism model
            return z + np.sqrt(x*x + y*y + z*z)
            
        # Off-diagonal components of the demagnetizing tensor
        Nxy = - 1/(4*np.pi)*np.log((G_func(a, b, c)*G_func(-a, -b, c)*G_func(-a, b, -c)*G_func(a, -b, -c))/\
            (G_func(-a, b, c)*G_func(a, -b, c)*G_func(a, b, -c)*G_func(a, b, c)))
                
        Nyx = - 1/(4*np.pi)*np.log((G_func(b, a, c)*G_func(-b, -a, c)*G_func(-b, a, -c)*G_func(b, -a, -c))/\
            (G_func(-b, a, c)*G_func(b, -a, c)*G_func(b, a, -c)*G_func(b, a, c)))
            
            
        result = [0]*self.len_x
        
        for i in range(self.len_x):
            # Values of f+ and f- for each H value
            H = pos[i*self.len_y: (1 + i)*self.len_y, 0]
            freq_ell = (abs(H) + Nxx*Ms)*(abs(H) + Nyy*Ms)
            
            try:
                freq_FMR = gamma*np.sqrt(freq_ell - ((Nxy + Nyx)*Ms)**2)
            except RuntimeWarning:
                # If the sign inside the square root is negative
                freq_FMR = 0
            
            
            delta = (self.freq_c - freq_FMR)**2 + 4*g**2
            freq_av = self.freq_c + freq_FMR
            
            # freq_s is f+ and freq_i is f-
            freq_s = 0.5*(freq_av + np.sqrt(delta))
            freq_i = 0.5*(freq_av - np.sqrt(delta))
            
            # Imitating S21 parameters with lorentzian centered on f+ and f- values
            result[i] = (self.lorentzian(pos[i*self.len_y: (1 + i)*self.len_y, 1], freq_s)+\
            self.lorentzian(pos[i*self.len_y: (1 + i)*self.len_y, 1], freq_i))*(self.S_max - self.S_min) + self.S_min
        
        return np.ravel(result)



    def slab_model_2D(self, H, g):
        # Rectangular prism model
        # H values, and the strentgh coupling (g)
        # Return values of f+, f-, and freq_FMR for each H value, freq_c and H value at freq_FMR = freq_c
        
        # Prism dimensions
        a = 0.25
        b = 3
        c = 2
        
        # Ferrimagnetic parameters (default: YIG)
        Ms = 0.176
        gamma = 28
        
        
        np.seterr(all='warn')
        warnings.filterwarnings('error')
        
            
        def f_func(x, y, z):
            # Function from the rectangular prism model
            return (np.sqrt(x*x + y*y + z*z)*z)/(x*y)
                
        # Diagonal components of the demagnetizing tensor
        Nzz = 2/(np.pi)*np.arctan(1/f_func(a, b, c))
        Nxx = 2/(np.pi)*np.arctan(1/f_func(c, b, a))
        Nyy = 2/(np.pi)*np.arctan(1/f_func(a, c, b))
          
          
        def G_func(x, y, z):
            # Function from the rectangular prism model
            return z + np.sqrt(x*x + y*y + z*z)
        
        # Off-diagonal components of the demagnetizing tensor
        Nxy = - 1/(4*np.pi)*np.log((G_func(a, b, c)*G_func(-a, -b, c)*G_func(-a, b, -c)*G_func(a, -b, -c))/\
            (G_func(-a, b, c)*G_func(a, -b, c)*G_func(a, b, -c)*G_func(a, b, c)))
                
        Nyx = - 1/(4*np.pi)*np.log((G_func(b, a, c)*G_func(-b, -a, c)*G_func(-b, a, -c)*G_func(b, -a, -c))/\
            (G_func(-b, a, c)*G_func(b, -a, c)*G_func(b, a, -c)*G_func(b, a, c)))
        
        
        freq_s = np.zeros_like(H)
        freq_i = np.zeros_like(H)
        freq_FMR = np.zeros_like(H)
        
        for i in range(len(H)):
            # Values of f+ and f- for each H value
            freq_ell = (abs(H[i]) + Nxx*Ms)*(abs(H[i]) + Nyy*Ms)
            
            try:
                freq_FMR[i] = gamma*np.sqrt(freq_ell - ((Nxy + Nyx)*Ms)**2)
            except RuntimeWarning:
                # If the sign inside the square root is negative
                freq_FMR[i] = 0.
            
            
            delta = (self.freq_c - freq_FMR[i])**2 + 4*g**2
            freq_av = self.freq_c + freq_FMR[i]
            
            # freq_s is f+ and freq_i is f-
            freq_s[i] = 0.5*(freq_av + np.sqrt(delta))
            freq_i[i] = 0.5*(freq_av - np.sqrt(delta))
            
            
        # Research of |H| (H_cross) value at f_FMR = f_c
        delta_cross = ((Nxx - Nyy)**2 + 4*(Nxy + Nyx)**2)*Ms**2 - (self.freq_c/gamma)**2
        H_av = (Nxx + Nyy)*Ms
                
        H_cross = 0.5*(H_av + np.sqrt(abs(delta_cross)))
            
        return freq_s, freq_i, freq_FMR, self.freq_c, H_cross



        
    def sphere_model_3D(self, pos, g):
        # Sphere model
        # Take a 2D list of all freq and H associated values (pos), and the strentgh coupling (g)
        # Example for pos: [[1, 1, 1, 2, 2, 2], [0, 0.1, 0.2, 0, 0.1, 0.2]]\
        # for two freq points equal to 1 and 2 and three H points equal to 0.1, 0.2, and 0.3
        # Return the artificial S21 parameters for each f and H values in 1D array
        
        # Ferrimagnetic parameters (default: YIG)
        Ms = 0.176
        gamma = 28
                    
                
        result = [0]*self.len_x
        
        for i in range(self.len_x):
            # Values of f+ and f- for each H value
            H = pos[i*self.len_y:(1 + i)*self.len_y, 0]
                    
            freq_FMR = gamma*H
            
            delta = (self.freq_c - freq_FMR)**2 + 4*g**2
            freq_av = self.freq_c + freq_FMR
            
            # freq_s is f+ and freq_i is f-
            freq_s = 0.5*(freq_av + np.sqrt(delta))
            freq_i = 0.5*(freq_av - np.sqrt(delta))
            
            result[i] = (self.lorentzian(pos[i*self.len_y:(1 + i)*self.len_y, 1], freq_s)+\
            self.lorentzian(pos[i*self.len_y:(1 + i)*self.len_y, 1], freq_i))*(self.S_max - self.S_min) + self.S_min
        
        return np.ravel(result)
        
        
        
    def sphere_model_2D(self, H, g):
        # Sphere model
        # H values, and the strentgh coupling (g)
        # Return values of f+, f-, and freq_FMR for each H value, freq_c and H value at freq_FMR = freq_c
        
        # Ferrimagnetic parameters (default: YIG)
        Ms = 0.176
        gamma = 28
        
        
        freq_s = np.zeros_like(H)
        freq_i = np.zeros_like(H)
        freq_FMR = np.zeros_like(H)
            
        for i in range(len(H)):
            # Values of f+ and f- for each H value
            freq_FMR[i] = gamma*(abs(H[i]) + Ms/3)
                
            delta = (self.freq_c - freq_FMR[i])**2 + 4*g**2
            freq_av = self.freq_c + freq_FMR[i]
            
            # freq_s is f+ and freq_i is f-
            freq_s[i] = 0.5*(freq_av + np.sqrt(delta))
            freq_i[i] = 0.5*(freq_av - np.sqrt(delta))
            
        
        # Research of |H| (H_cross) value at f_FMR = f_c 
        H_cross = self.freq_c/gamma - Ms/3
            
        return freq_s, freq_i, freq_FMR, self.freq_c, H_cross




if __name__ == '__main__':
    nbp_freq = 3001
    nbp_H = 1401
    
    
    H_file = "C:/Users/guill/Documents/Thèse/Slab/Measures/TEC03_BM_5.5/H_values.txt"
    freq_file = "C:/Users/guill/Documents/Thèse/Slab/Measures/TEC03_BM_5.5/f_values.txt"
    S21_file = "C:/Users/guill/Documents/Thèse/Slab/Measures/TEC03_BM_5.5/S/S21/Intensity.txt"

    
    H_table = np.genfromtxt(H_file, names=True, delimiter = '\n')
    f_table = np.genfromtxt(freq_file, names=True, delimiter = '\n')
    S210 = np.genfromtxt(S21_file, delimiter = ',')
    
    H_name = H_table.dtype.names[0]
    f_name = f_table.dtype.names[0]
    
    H = H_table[H_name]
    f = f_table[f_name]
    
    
    model = models()
    model.search_freq_c(f, [S210[int(len(H)/2)], S210[0]])
    
    
    # Meshgrid for a colormap
    freqg0, Hg0 = np.meshgrid(f, H)
    pos = np.array(list(zip(np.ravel(Hg0), np.ravel(freqg0))))
    S21 = np.ravel(S210)
    
    """
    fig, ax = plt.subplots()
    im = ax.pcolormesh(Hg0, freqg0, S210, cmap='hot', vmin=-100, vmax = -20, shading='auto')
    ax.set_xlabel('Magnetic Field [T]', fontsize=20)
    ax.set_ylabel('Frequency [GHz]', fontsize=20)
    cb = plt.colorbar(im, ax=ax, boundaries=np.linspace(-140, -20, 100), ticks=np.linspace(-140, -20, 6))
    cb.ax.set_ylabel('S\u2082\u2081 [dB]', rotation=-90, size=20, labelpad=10)
    cb.ax.tick_params(labelsize=15) 
    
    plt.show()
    """
    
    popt, pcov = scp.curve_fit(model.slab_model_3D, pos, S21, bounds=(0, 2), maxfev=600)
    popt = popt[0]
    """
    fig, ax = plt.subplots(2, 1)

    im = ax[0].pcolormesh(Hg0, freqg0, S210, cmap='hot', vmin=-100, vmax = -20, shading='auto')
    ax[0].set_xlabel('Magnetic Field [T]', fontsize=20)
    ax[0].set_ylabel('Frequency [GHz]', fontsize=20)
    cb = plt.colorbar(im, ax=ax[0], boundaries=np.linspace(-140, -20, 100), ticks=np.linspace(-140, -20, 6))
    cb.ax.set_ylabel('S\u2082\u2081 [dB]', rotation=-90, size=20, labelpad=10)
    cb.ax.tick_params(labelsize=15) 
    
    
    S21_test2 = model.slab_model_3D(pos, popt)
    S21_test2 = S21_test2.reshape(len(Hg0), len(Hg0[0]))
    
    im = ax[1].pcolormesh(Hg0, freqg0, S21_test2, cmap='hot', vmin=-100, vmax = -20, shading="auto")
    ax[1].set_xlabel('Magnetic Field [T]', fontsize=20)
    ax[1].set_ylabel('Frequency [GHz]', fontsize=20)
    cb = plt.colorbar(im, ax=ax[1], boundaries=np.linspace(-140, -20, 100), ticks=np.linspace(-140, -20, 6))
    cb.ax.set_ylabel('S\u2082\u2081 [dB]', rotation=-90, size=20, labelpad=10)
    cb.ax.tick_params(labelsize=15) 
    

    plt.show()
    """
    
    fig, ax = plt.subplots()
    im = ax.pcolormesh(Hg0, freqg0, S210, cmap='hot', vmin=-100, vmax = -20, shading='auto')
    ax.set_xlabel('Magnetic Field [T]', fontsize=20)
    ax.set_ylabel('Frequency [GHz]', fontsize=20)
    cb = plt.colorbar(im, ax=ax, boundaries=np.linspace(-140, -20, 100), ticks=np.linspace(-140, -20, 6))
    cb.ax.set_ylabel('S\u2082\u2081 [dB]', rotation=90, size=20, labelpad=10)
    cb.ax.tick_params(labelsize=15) 
    
    over2 = model.slab_model_2D(H, popt)
    ax.plot(H, over2[0], 'g', H, over2[1], 'g', H, over2[2], 'g--',\
        [H[0], H[-1]], [over2[3], over2[3]], 'g--', lw=1)
    
    ax.arrow(over2[4], over2[3]-popt, 0, 2*popt, length_includes_head = True,\
        linewidth = 0.01, head_width=0.006, head_length=0.2, color='w')
    ax.arrow(over2[4], over2[3]+popt, 0, -2*popt, length_includes_head = True,\
        linewidth = 0.01, head_width=0.006, head_length=0.2, color='w')
    ax.annotate(f'g/\u03C0 = {round(popt, 2)}', (over2[4]+0.01, over2[3]+0.1), fontsize=15, c='w')
    
    ax.annotate(f'f\u209A = {round(over2[3], 2)}', (H[0]+1e-3, over2[3]+0.1), fontsize=15, c='w')
    
    ax.annotate('f\u2098', (H[0]+1e-3, f[-1]-0.5), fontsize=15, c='k')
    
    ax.annotate('f\u208A', (-over2[4], over2[3]+0.1+popt), fontsize=15, c='w')
    
    ax.annotate('f\u208B', (-over2[4], over2[3]-0.4-popt), fontsize=15, c='w')
    
    ax.set_ylim(f[0], f[-1])
    ax.tick_params(axis='both', which='major', labelsize=15)
    
    plt.show()
    