from inspect import modulesbyfile
import numpy as np
import matplotlib.pyplot as plt
import csv
import pandas as pd 
import scipy.optimize as scp
import warnings



class models(object):
    def __init__(self):
        self.freq_c =None
        
        self.len_x = 3001
        self.len_y = 1401
        self.S_max = -35
        self.S_min = -100
        
    

    def lorentzian(self, x, x0):
        return 1/(1 + 4*(x - x0)**2/0.01)
    
    
    
    def search_freq_c(self, freq, S21):
        S21_first = S21[0]
        S21_last = S21[1]
        
        
        def covid(freq, S21):
            self.S21_min = np.mean(S21)
            self.S21_max = max(S21)
        
            S21 = np.maximum(S21, self.S21_min)
            
            
            cov = np.zeros_like(freq)
            counter = 0
            for i in range(2, len(freq)):
                lolo = self.lorentzian(freq, freq[i])*(self.S21_max - self.S21_min) + self.S21_min
                cov[i] = np.cov(S21, lolo)[0, 1]
                
                if cov[i-2] < cov[i-1] > cov[i]:
                    if counter == 0:
                        counter += 1
                    else:
                        return freq[i]
                    
        
        freq_c_first = covid(freq, S21_first)
        freq_c_last = covid(freq, S21_last)
        
        self.freq_c = (freq_c_first + freq_c_last)/2
                        
            
        
        print(self.freq_c)    
        plt.plot(freq, S21_first, freq, S21_last, freq, self.lorentzian(freq, self.freq_c)*\
            (self.S21_max - self.S21_min) + self.S21_min)
        plt.show()
        
    
        
    def slab_model_3D(self, pos, g):
        a = 0.25
        b = 3
        c = 2
        np.seterr(all='warn')
        warnings.filterwarnings('error')
        Ms = 0.176
        gamma = 28
                
                
        def f_func(x, y, z):
            return (np.sqrt(x*x + y*y + z*z)*z)/(x*y)
            
        Nzz = 2/(np.pi)*np.arctan(1/f_func(a, b, c))
        Nxx = 2/(np.pi)*np.arctan(1/f_func(c, b, a))
        Nyy = 2/(np.pi)*np.arctan(1/f_func(a, c, b))
                
                
        def G_func(x, y, z):
            return z + np.sqrt(x*x + y*y + z*z)
            
        Nxy = - 1/(4*np.pi)*np.log((G_func(a, b, c)*G_func(-a, -b, c)*G_func(-a, b, -c)*G_func(a, -b, -c))/\
            (G_func(-a, b, c)*G_func(a, -b, c)*G_func(a, b, -c)*G_func(a, b, c)))
                
        Nyx = - 1/(4*np.pi)*np.log((G_func(b, a, c)*G_func(-b, -a, c)*G_func(-b, a, -c)*G_func(b, -a, -c))/\
            (G_func(-b, a, c)*G_func(b, -a, c)*G_func(b, a, -c)*G_func(b, a, c)))
            
            
        result = [0]*self.len_x
        for i in range(self.len_x):
            H = pos[i*self.len_y: (1 + i)*self.len_y, 0]
            freq_ell = (abs(H) + Nxx*Ms)*(abs(H) + Nyy*Ms)
            
            try:
                freq_FMR = gamma*np.sqrt(freq_ell - ((Nxy + Nyx)*Ms)**2)
            except RuntimeWarning:
                freq_FMR = 0
                
            delta = (self.freq_c**2 - freq_FMR**2)**2/4 + 4*self.freq_c*freq_FMR*g**2
            freq_av = (self.freq_c**2 + freq_FMR**2)/2

            # Hybridized frequencies, superior frenquency (freq_s) and inferior frequency (freq_i)
            freq_s = np.sqrt(freq_av + np.sqrt(delta))
            try:
                freq_i =  np.sqrt(freq_av - np.sqrt(delta))
            except RuntimeWarning:
                freq_i = self.S_min
            result[i] = (self.lorentzian(pos[i*self.len_y: (1 + i)*self.len_y, 1], freq_s)+\
            self.lorentzian(pos[i*self.len_y: (1 + i)*self.len_y, 1], freq_i))*(self.S_max - self.S_min) + self.S_min
        return np.ravel(result)




    def slab_model_2D(self, H, g):
        a = 0.25
        b = 3
        c = 2
        np.seterr(all='warn')
        warnings.filterwarnings('error')
        
        gamma = 28
        Ms = 0.176
            
        def f_func(x, y, z):
            return (np.sqrt(x*x + y*y + z*z)*z)/(x*y)
                
        Nzz = 2/(np.pi)*np.arctan(1/f_func(a, b, c))
        Nxx = 2/(np.pi)*np.arctan(1/f_func(c, b, a))
        Nyy = 2/(np.pi)*np.arctan(1/f_func(a, c, b))
        
                
                
        def G_func(x, y, z):
            return z + np.sqrt(x*x + y*y + z*z)
            
        Nxy = - 1/(4*np.pi)*np.log((G_func(a, b, c)*G_func(-a, -b, c)*G_func(-a, b, -c)*G_func(a, -b, -c))/\
            (G_func(-a, b, c)*G_func(a, -b, c)*G_func(a, b, -c)*G_func(a, b, c)))
                
        Nyx = - 1/(4*np.pi)*np.log((G_func(b, a, c)*G_func(-b, -a, c)*G_func(-b, a, -c)*G_func(b, -a, -c))/\
            (G_func(-b, a, c)*G_func(b, -a, c)*G_func(b, a, -c)*G_func(b, a, c)))
        
        
            
        freq_s = np.zeros_like(H)
        freq_i = np.zeros_like(H)
        freq_FMR = np.zeros_like(H)
        
        
        for i in range(len(H)):
            freq_ell = (abs(H[i]) + Nxx*Ms)*(abs(H[i]) + Nyy*Ms)
            try:
                freq_FMR[i] = gamma*np.sqrt(freq_ell - ((Nxy + Nyx)*Ms)**2)
            except RuntimeWarning:
                freq_FMR[i] = 0.
                
                
            
            delta = (self.freq_c**2 - freq_FMR[i]**2)**2/4 + 4*self.freq_c*freq_FMR[i]*g**2
            freq_av = (self.freq_c**2 + freq_FMR[i]**2)/2

            # Hybridized frequencies, superior frenquency (freq_s) and inferior frequency (freq_i)
            freq_s[i] = np.sqrt(freq_av + np.sqrt(delta))
            try:
                freq_i[i] =  np.sqrt(freq_av - np.sqrt(delta))
            except RuntimeWarning:
                freq_i[i] = np.nan
        return freq_s, freq_i, freq_FMR, self.freq_c



        
    def sphere_model_3D(self, pos, g):
        gamma = 28
        Ms = 0.176
                    
                
        result = [0]*self.len_x
        for i in range(self.len_x):
            H = pos[i*self.len_y:(1 + i)*self.len_y, 0]
                    
            freq_FMR = gamma*H
                    
            delta = (self.freq_c**2 - freq_FMR**2)**2/4 + 4*self.freq_c*freq_FMR*g**2
            freq_av = (self.freq_c**2 + freq_FMR**2)/2

            # Hybridized frequencies, superior frenquency (freq_s) and inferior frequency (freq_i)
            freq_s = np.sqrt(freq_av + np.sqrt(delta))
            freq_i =  np.sqrt(freq_av - np.sqrt(delta))
            result[i] = (self.lorentzian(pos[i*self.len_y:(1 + i)*self.len_y, 1], freq_s)+\
            self.lorentzian(pos[i*self.len_y:(1 + i)*self.len_y, 1], freq_i))*(self.S_max - self.S_min) + self.S_min
        return np.ravel(result)
        
        
        
    def sphere_model_2D(self, H, g):
        gamma = 28
        Ms = 0.176
        
        freq_s = np.zeros_like(H)
        freq_i = np.zeros_like(H)
        freq_FMR = np.zeros_like(H)
            
        for i in range(len(H)):
            freq_FMR[i] = gamma*(abs(H[i]) + Ms/3)
                    
            delta = (self.freq_c**2 - freq_FMR[i]**2)**2/4 + 4*self.freq_c*freq_FMR[i]*g**2
            freq_av = (self.freq_c**2 + freq_FMR[i]**2)/2

            # Hybridized frequencies, superior frenquency (freq_s) and inferior frequency (freq_i)
            freq_s[i] = np.sqrt(freq_av + np.sqrt(delta))
            freq_i[i] =  np.sqrt(freq_av - np.sqrt(delta))
        return freq_s, freq_i, freq_FMR, self.freq_c




if __name__ == '__main__':
    nbp_freq = 3001
    nbp_H = 1401
    
    
    
    H_file = "C:/Users/guill/Documents/Thèse/Slab/Measures/TEC03_BM_2.5/H_values.txt"
    freq_file = "C:/Users/guill/Documents/Thèse/Slab/Measures/TEC03_BM_2.5/f_values.txt"
    S21_file = "C:/Users/guill/Documents/Thèse/Slab/Measures/TEC03_BM_2.5/S/S21/Intensity.txt"

    
    H_table = np.genfromtxt(H_file, names=True, delimiter = '\n')
    f_table = np.genfromtxt(freq_file, names=True, delimiter = '\n')
    S210 = np.genfromtxt(S21_file, delimiter = ',')
    
    H_name = H_table.dtype.names[0]
    f_name = f_table.dtype.names[0]
    
    H = H_table[H_name]
    f = f_table[f_name]
    
    
    model = models()
    model.search_freq_c(f, [S210[0], S210[-1]])
    
    
    # Meshgrid for a colormap
    freqg0, Hg0 = np.meshgrid(f, H)
    pos = np.array(list(zip(np.ravel(Hg0), np.ravel(freqg0))))
    S21 = np.ravel(S210)
    
    """
    fig, ax = plt.subplots()
    S21_test2 = models().slab_model_3D(pos, 0.68)
    S21_test2 = S21_test2.reshape(len(Hg0), len(Hg0[0]))
    
    im = ax.pcolormesh(Hg0, freqg0, S21_test2, cmap='hot', vmin=-80, vmax = -20, shading='auto')
    ax.set_xlabel('Voltage [V]')
    ax.set_ylabel('Frequency [GHz]')
    cb = plt.colorbar(im, ax=ax, boundaries=np.linspace(-140, -40, 100))
    cb.ax.set_title('S\u2082\u2081 [dB]')
    
    ax.set_ylim(f[0], f[-1])
    ax.tick_params(axis='both', which='major', labelsize=15)
    
    plt.show()
    """
    popt, pcov = scp.curve_fit(model.slab_model_3D, pos, S21, bounds=(0, 2), maxfev=600)
    print(popt)
    
    fig, ax = plt.subplots(2, 1)

    im = ax[0].pcolormesh(Hg0, freqg0, S210, cmap='hot', vmin=-80, vmax = -20, shading='auto')
    ax[0].set_xlabel('Voltage [V]')
    ax[0].set_ylabel('Frequency [GHz]')
    cb = plt.colorbar(im, ax=ax[0], boundaries=np.linspace(-140, -40, 100))
    cb.ax.set_title('S\u2082\u2081 [dB]')
    
    
    S21_test2 = model.slab_model_3D(pos, popt)
    S21_test2 = S21_test2.reshape(len(Hg0), len(Hg0[0]))
    
    im = ax[1].pcolormesh(Hg0, freqg0, S21_test2, cmap='hot', vmin=-80, vmax = -20, shading='auto')
    ax[1].set_xlabel('Voltage [V]')
    ax[1].set_ylabel('Frequency [GHz]')
    cb = plt.colorbar(im, ax=ax[1], boundaries=np.linspace(-140, -40, 100))
    cb.ax.set_title('S\u2082\u2081 [dB]')


    plt.show()
    
    fig, ax = plt.subplots()
    im = ax.pcolormesh(Hg0, freqg0, S210, cmap='hot', vmin=-100, vmax = -20, shading='auto')
    ax.set_xlabel('Magnetic Field [T]', fontsize=20)
    ax.set_ylabel('Frequency [GHz]', fontsize=20)
    cb = plt.colorbar(im, ax=ax, boundaries=np.linspace(-140, -20, 100), ticks=np.linspace(-140, -20, 6))
    cb.ax.set_ylabel('S\u2082\u2081 [dB]', rotation=-90, size=20, labelpad=10)
    cb.ax.tick_params(labelsize=15) 
    
    
    over2 = model.slab_model_2D(H, popt)
    ax.plot(H, over2[0], 'g', H, over2[1], 'g', H, over2[2], 'g--',\
        [H[0], H[-1]], [over2[3], over2[3]], 'g--', lw=1)
    
    
    ax.set_ylim(f[0], f[-1])
    ax.tick_params(axis='both', which='major', labelsize=15)
    
    plt.show()