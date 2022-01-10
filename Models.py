import numpy as np
import matplotlib.pyplot as plt
import csv
import pandas as pd 
import scipy.optimize as scp



class models(object):
    def __init__(self):
        self.freq_c =4.35
    
        
        
    def Lorentzian(self, x, x0):
        return 1/(1 + 4*(x - x0)**2/0.01)
        
        
        
    def Slab_model_3D(self, pos, g):
        a = 0.25
        b = 3
        c = 2
            
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
            freq_ell = (H + Nxx*Ms)*(H + Nzz*Ms)
            
            freq_FMR = gamma*np.sqrt(freq_ell - ((Nxy + Nyx)*Ms)**2)
                
            delta = (self.freq_c**2 - freq_FMR**2)**2/4 + 4*self.freq_c*freq_FMR*g**2
            freq_av = (self.freq_c**2 + freq_FMR**2)/2

            # Hybridized frequencies, superior frenquency (freq_s) and inferior frequency (freq_i)
            freq_s = np.sqrt(freq_av + np.sqrt(delta))
            freq_i =  np.sqrt(freq_av - np.sqrt(delta))
            result[i] = (self.Lorentzian(pos[i*self.len_y: (1 + i)*self.len_y, 1], freq_s)+\
            self.Lorentzian(pos[i*self.len_y: (1 + i)*self.len_y, 1], freq_i))*(self.S_max - self.S_min) + self.S_min
        return np.ravel(result)




    def Slab_model_2D(self, H, g):
        a = 0.25
        b = 3
        c = 2
        
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
            """
            freq_ell = (abs(H[i]) - Nzz*Ms)*(abs(H[i]) - Nzz*Ms)
            freq_FMR[i] = gamma*np.sqrt(freq_ell) + gamma*Ms/3
            """
            
            term1 = (Nxx - Nzz)*Ms
            term2 = (Nyy - Nzz)*Ms
            term3 = ((Nxy + Nyx)*Ms)**2
            """
            Hz = 0.5*(-(term1 + term2) + np.sqrt((term1 - term2)**2 + 4*(term3 + H[i]**2)))
            
            freq_ell = (Hz + (Nxx - Nzz)*Ms)*(Hz + (Nyy - Nzz)*Ms)
            freq_FMR[i] = gamma*np.sqrt(freq_ell - ((Nxy + Nyx)*Ms)**2)
            
            freq_FMR[i] = gamma*Hz
            """
            
            
            freq_ell = (abs(H[i]) + Nxx*Ms)*(abs(H[i]) + Nyy*Ms)
            freq_FMR[i] = gamma*np.sqrt(freq_ell - ((Nxy + Nyx)*Ms)**2)
            
        
            """
            freq_FMR[i]  = abs(gamma*H[i]) + gamma*Ms/3
            """
            delta = (self.freq_c**2 - freq_FMR[i]**2)**2/4 + 4*self.freq_c*freq_FMR[i]*g**2
            freq_av = (self.freq_c**2 + freq_FMR[i]**2)/2

            # Hybridized frequencies, superior frenquency (freq_s) and inferior frequency (freq_i)
            freq_s[i] = np.sqrt(freq_av + np.sqrt(delta))
            freq_i[i] =  np.sqrt(freq_av - np.sqrt(delta))
        return freq_s, freq_i, freq_FMR, self.freq_c




    def Slab_model_2D_try(self, H, g):
        a = 0.25
        b = 3
        c = 2
        
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
            """
            freq_ell = (abs(H[i]) - Nzz*Ms)*(abs(H[i]) - Nzz*Ms)
            freq_FMR[i] = gamma*np.sqrt(freq_ell - (Nzz*Ms)**2)
            """
            
            term1 = (Nxx - Nzz)*Ms
            term2 = (Nyy - Nzz)*Ms
            term3 = ((Nxy + Nyx)*Ms)**2
            """
            Hz = 0.5*(-(term1 + term2) + np.sqrt((term1 - term2)**2 + 4*(term3 + H[i]**2)))
            
            freq_ell = (Hz + (Nxx - Nzz)*Ms)*(Hz + (Nyy - Nzz)*Ms)
            freq_FMR[i] = gamma*np.sqrt(freq_ell - ((Nxy + Nyx)*Ms)**2)
            
            freq_FMR[i] = gamma*Hz
            """
            
            
            freq_ell = (abs(H[i]) + (Nxx - Nzz)*Ms)*(abs(H[i]) + (Nyy - Nzz)*Ms)
            freq_FMR[i] = gamma*np.sqrt(freq_ell - term1*term2)
            
        
            """
            freq_FMR[i]  = abs(gamma*H[i]) + gamma*Ms/3
            """
            delta = (self.freq_c**2 - freq_FMR[i]**2)**2/4 + 4*self.freq_c*freq_FMR[i]*g**2
            freq_av = (self.freq_c**2 + freq_FMR[i]**2)/2

            # Hybridized frequencies, superior frenquency (freq_s) and inferior frequency (freq_i)
            freq_s[i] = np.sqrt(freq_av + np.sqrt(delta))
            freq_i[i] =  np.sqrt(freq_av - np.sqrt(delta))
        return freq_s, freq_i, freq_FMR, self.freq_c
    
    
    
    
    def Slab_model_2D_try2(self, H, g):
        a = 0.25
        b = 3
        c = 2
        
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
            """
            freq_ell = (abs(H[i]) - Nzz*Ms)*(abs(H[i]) - Nzz*Ms)
            freq_FMR[i] = gamma*np.sqrt(freq_ell - (Nzz*Ms)**2)
            """
            
            term1 = (Nxx - Nzz)*Ms
            term2 = (Nyy - Nzz)*Ms
            term3 = ((Nxy + Nyx)*Ms)**2
            """
            Hz = 0.5*(-(term1 + term2) + np.sqrt((term1 - term2)**2 + 4*(term3 + H[i]**2)))
            
            freq_ell = (Hz + (Nxx - Nzz)*Ms)*(Hz + (Nyy - Nzz)*Ms)
            freq_FMR[i] = gamma*np.sqrt(freq_ell - ((Nxy + Nyx)*Ms)**2)
            
            freq_FMR[i] = gamma*Hz
            """
            
            
            freq_ell = (abs(H[i]) + (Nxx - Nzz)*Ms)*(abs(H[i]) + (Nyy - Nzz)*Ms)
            freq_FMR[i] = gamma*np.sqrt(freq_ell + ((Nxy + Nyx)*Ms)**2 - 3*term1*term2)
            
        
            """
            freq_FMR[i]  = abs(gamma*H[i]) + gamma*Ms/3
            """
            delta = (self.freq_c**2 - freq_FMR[i]**2)**2/4 + 4*self.freq_c*freq_FMR[i]*g**2
            freq_av = (self.freq_c**2 + freq_FMR[i]**2)/2

            # Hybridized frequencies, superior frenquency (freq_s) and inferior frequency (freq_i)
            freq_s[i] = np.sqrt(freq_av + np.sqrt(delta))
            freq_i[i] =  np.sqrt(freq_av - np.sqrt(delta))
        return freq_s, freq_i, freq_FMR, self.freq_c



        
    def Sphere_model_3D(self, pos, g):
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
            result[i] = (self.Lorentzian(pos[i*self.len_y:(1 + i)*self.len_y, 1], freq_s)+\
            self.Lorentzian(pos[i*self.len_y:(1 + i)*self.len_y, 1], freq_i))*(self.S_max - self.S_min) + self.S_min
        return np.ravel(result)
        
        
        
    def Sphere_model_2D(self, H, g):
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
    
    
    
    H_file = "C:/Users/guill/Documents/Thèse/Slab/Measures/TEC03_BM_4.5/H_values.txt"
    freq_file = "C:/Users/guill/Documents/Thèse/Slab/Measures/TEC03_BM_4.5/f_values.txt"
    S21_file = "C:/Users/guill/Documents/Thèse/Slab/Measures/TEC03_BM_4.5/S/S21/Intensity.txt"

    
    H_table = np.genfromtxt(H_file, names=True, delimiter = '\n')
    f_table = np.genfromtxt(freq_file, names=True, delimiter = '\n')
    S210 = np.genfromtxt(S21_file, delimiter = ',')
    
    H_name = H_table.dtype.names[0]
    f_name = f_table.dtype.names[0]
    
    H = H_table[H_name]
    f = f_table[f_name]
    
    # Meshgrid for a colormap
    freqg0, Hg0 = np.meshgrid(f, H)
    """
    freqg = freqg0[int(nbp_freq/5*0.04):int(nbp_freq/5*0.23), int(nbp_freq/10*2.5):int(nbp_freq/10*8)]
    Hg = Hg0[int(nbp_freq/5*0.04):int(nbp_freq/5*0.23), int(nbp_freq/10*2.5):int(nbp_freq/10*8)]
    S21 = S210[int(nbp_freq/5*0.04):int(nbp_freq/5*0.23), int(nbp_freq/10*2.5):int(nbp_freq/10*8)]
    """
    """
    fig, ax = plt.subplots(2, 1)

    im = ax[0].pcolormesh(Vg, freqg, S21, cmap='hot', vmin=-80, vmax = -20, shading='auto')
    ax[0].set_xlabel('Voltage [V]')
    ax[0].set_ylabel('Frequency [GHz]')
    cb = plt.colorbar(im, ax=ax[0], boundaries=np.linspace(-140, -40, 100))
    cb.ax.set_title('S\u2082\u2081 [dB]')
    
    pos = np.array(list(zip(np.ravel(Hg), np.ravel(freqg))))
    S21_test2 = Slab_model_3D(pos, 0.75, len(Hg), len(Hg[0]))

    S21_test2 = S21_test2.reshape(len(Hg), len(Hg[0]))
    
    im = ax[1].pcolormesh(Vg, freqg, S21_test2, cmap='hot', vmin=-80, vmax = -20, shading='auto')
    ax[1].set_xlabel('Voltage [V]')
    ax[1].set_ylabel('Frequency [GHz]')
    cb = plt.colorbar(im, ax=ax[1], boundaries=np.linspace(-140, -40, 100))
    cb.ax.set_title('S\u2082\u2081 [dB]')


    plt.show()"""
    
    g = 0.65
    
    fig, ax = plt.subplots()
    im = ax.pcolormesh(Hg0, freqg0, S210, cmap='hot', vmin=-100, vmax = -20, shading='auto')
    ax.set_xlabel('Magnetic Field [T]', fontsize=20)
    ax.set_ylabel('Frequency [GHz]', fontsize=20)
    cb = plt.colorbar(im, ax=ax, boundaries=np.linspace(-140, -20, 100), ticks=np.linspace(-140, -20, 6))
    cb.ax.set_ylabel('S\u2082\u2081 [dB]', rotation=-90, size=20, labelpad=10)
    cb.ax.tick_params(labelsize=15) 
    
    """
    over1 = models().Sphere_model_2D(H, g)
    ax.plot(H, over1[0], 'b', H, over1[1], 'b', H, over1[2], 'b--',\
        [H[0], H[-1]], [over1[3], over1[3]], 'b--', lw=1)
    """
    
    over2 = models().Slab_model_2D(H, g)
    ax.plot(H, over2[0], 'g', H, over2[1], 'g', H, over2[2], 'g--',\
        [H[0], H[-1]], [over2[3], over2[3]], 'g--', lw=1)
    
    """
    over3 = models().Slab_model_2D_try(H, g)
    ax.plot(H, over3[0], 'w', H, over3[1], 'w', H, over3[2], 'w--',\
        [H[0], H[-1]], [over3[3], over3[3]], 'w--', lw=0.5)
    
    over4 = models().Slab_model_2D_try2(H, g)
    ax.plot(H, over4[0], 'c', H, over4[1], 'c', H, over4[2], 'c--',\
        [H[0], H[-1]], [over4[3], over4[3]], 'c--', lw=0.5)
    """
    
    
    ax.set_ylim(f[0], f[-1])
    ax.tick_params(axis='both', which='major', labelsize=15)
    
    print("Hello")
    plt.show()

    
        