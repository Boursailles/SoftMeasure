from inspect import modulesbyfile
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as scp
from scipy.signal import savgol_filter
import warnings




#******************************************************************************************************#
# This program is working with Interface.py file for SoftMeasure.
# It contains physics models of the photon-magnon hybridization and fit functions
#******************************************************************************************************#




class models(object):
    """
    Contains physics models of the photon-magnon hybridization, fit functions, and Q-factor calculation
    """
    
    def __init__(self):
        self.freq_c = None
        
        
    
    def lorentzian(self, x, x0, sigma):
        """
        Lorentzian equation which permits to imitate S21 parameter
        
        Parameters
        ----------
        x: 1D-array
        
        x0: float
        
        sigma: float
        
        Returns
        ----------
        1D-array
            Lorentzian curve
        """
        return 1/(1 + (2*(x - x0)/sigma)**2)
    
    
    
    def search_freq_c(self, freq, S21):
        """
        Method which permits to find out the cavity frequency (BM) with doing an average
        on two sets (for two different H values) of S21 values with respect to the frequency
        
        Parameters
        ----------
        freq: 1D-array
        
        S21: 2D-array
            Each dimension is a 1D-array of S21 values for Hmax and H = 0 respectively
        """
        
        S21_first = S21[0]
        S21_last = S21[1]
        
        
        def covid(freq, S21):
            """
            Function which permits to find out the cavity frequency (BM) using covariance method.
            This method permits to reduce the noise and show better peak modes

            Parameters
            ----------
            freq: 1D-array
            
            S21: 1D-array
            
            Returns
            ----------
            float
                Cavity frequency, BM mode
            """
            
            # Suppress S21 values below the average of S21 values for a better fit
            #self.S21_min = min(S21)
            self.S21_max = max(S21)
        
            S21 = np.maximum(S21, np.mean(S21)) - np.mean(S21)
            
            
            # Using covariance of S21 curve with lorentzian function
            cov = np.zeros_like(freq)
            counter = 0
            for i in range(2, len(freq)):
                lolo = self.lorentzian(freq, freq[i], 0.1)*abs(self.S21_max - self.S21_min)
                cov[i] = np.cov(S21, lolo)[0, 1]
                if cov[i-2] < cov[i-1] > cov[i] and\
                    (abs(cov[i-1] - cov[i-2]) > 4e-4 or abs(cov[i-1] - cov[i]) > 4e-4):
                    # Detection of a mode
                    if counter == 0:
                        # This is a DM mode, we don't care about it
                        counter += 1
                    else:
                        # This is a BM mode, the frequency of the cavity which interests us
                        return freq[i]
        
        
        freq_c_first = covid(freq, S21_first)
        Q_values = self.calc_Q_factor(freq, freq_c_first, S21_first)
        
        Q_factor_first, freq_c_first, sigma, S21max, S21min, freq_gap, idx_min, idx_max = Q_values
        self.sigma = sigma
        print(self.sigma)
        
        
        params = {'mathtext.default': 'regular' }
        plt.rcParams.update(params)
        
        plt.plot(freq[idx_min:idx_max], S21_first[idx_min:idx_max], 'o', label='Measured transmission')
        
        freq_fit = np.linspace(freq[idx_min], freq[idx_max], 5000)
        plt.plot(freq_fit, self.lorentzian(freq_fit, freq_c_first, sigma)*(S21max - S21min) + S21min,\
            label='Fitted transmission')
        
        plt.arrow(freq_c_first-freq_gap, S21max-3, 2*freq_gap, 0, length_includes_head = True,\
            linewidth = 1, head_width=0.06, head_length=0.002, color='k')
        plt.arrow(freq_c_first+freq_gap, S21max-3, -2*freq_gap, 0, length_includes_head = True,\
            linewidth = 1, head_width=0.06, head_length=0.002, color='k')
        plt.annotate('$\Delta f_{-3dB}$'+f' = {round(2*freq_gap, 3)} GHz',\
            (freq_c_first-0.008, S21max-3+0.1), fontsize=30)
        
        plt.annotate(f'Q = {int(Q_factor_first)}',\
            (freq[idx_min], S21max-0.1), fontsize=30)
        
        plt.xlabel('Frequency [GHz]', fontsize=30)
        plt.ylabel('$S_{21}$ [dB]', fontsize=30)
        plt.tick_params(axis='both', which='major', labelsize=30)
        
        plt.legend(prop={'size': 30})
        
        freq_c_last = covid(freq, S21_last)
        freq_c_last = self.calc_Q_factor(freq, freq_c_last, S21_last)[1]
        
        # Average of the two BM modes found out for each H values
        self.freq_c = (freq_c_first + freq_c_last)/2
        print(self.freq_c)

        self.S_min = S21min
        self.S_max = S21max
        
        
        
    def calc_Q_factor(self, freq, freq_c, S21):
        """
        Method which permits to find out the accurate cavity frequency (BM) and to calculate
        the quality factor

        Parameters
        ----------
        freq: 1D-array
            
        freq_c: float
        
        S21: 1D-array
            
        Returns
        ----------
        Q_factor: float
        
        freq_c: float
        
        sigma: float
        
        S21max: float
            Maximum value of S21 fitted
            
        S21min: float
            Minimum value of S21 fitted
            
        freq_gap: float
            Full Width at Half Maximum
            
        idx_min: float
            Minimum index of the crossed curve
            
        idx_max: float
            Maximum index of the crossed curve
        """
        
        def find_nearest(array, value):
            """
            Function finding out the index of the nearest value of the setting one in a list

            Parameters
            ----------
            array: 1D-array
                
            value: float
                            
            Returns
            ----------
            idx: int
            """
            
            array = np.asarray(array)
            idx = (np.abs(array - value)).argmin()
            return idx
        
        
        idx = find_nearest(freq, freq_c)
        S21_mean = np.mean(S21)
        
        
        # Keep curve piece where S21 values are decreased less than 4 dB with respect to the peak
        for i in range(idx, len(freq)):
            if S21[idx] - S21[i] > 4:
                idx_max = i
                break
            
        for i in range(idx, 0, -1):
            if S21[idx] - S21[i] > 4:
                idx_min = i
                break
        
        idx_mean = max(abs(idx - idx_min), abs(idx - idx_max))
        idx_min = idx - idx_mean
        idx_max = idx + idx_mean
        
        
        def S21_artificial(x, freq_c, sigma, S21max, S21min):
            """
            Function modelizing S21 curve with lorentzian formula

            Parameters
            ----------
            x: 1D-array
                
            freq_c: float
            
            sigma: float
            
            S21max: float
            
            S21min: float
                            
            Returns
            ----------
            S21: 1D-array
            """
            
            return self.lorentzian(x, freq_c, sigma)*(S21max - S21min) + S21min
        
        
        popt, pcov = scp.curve_fit(S21_artificial, freq[idx_min:idx_max], S21[idx_min:idx_max],\
            p0=(freq_c, 0.08, S21[idx], S21[idx_min]))
        
        freq_c = popt[0]
        
        
        def inversed_lorentzian(S21_3dB, sigma, S21max, S21min):
            """
            Inversed lorentzian equation which permits to find out the frequency gap from cavity frequency
            for an input S21 value
            
            Parameters
            ----------
            S21: float
            
            x0: float
            
            Returns
            ----------
            float
                Associated frequency
            """
            return abs(np.sqrt(((S21max - S21min)/(S21_3dB - S21min) - 1))/2*sigma)
        
        
        freq_gap = inversed_lorentzian(popt[2]-3, *popt[1:])
        Q_factor = freq_c/freq_gap
        
        return Q_factor, popt, freq_gap, idx_min, idx_max
        
    
      
    def Slab_model_3D(self, pos, g):
        """
        Rectangular prism model
        
        Parameters
        ----------
        pos: 2D-array
            First 1D-array contains frequency values for each H values in the second 1D-array
            
        g: float
            Strentgh coupling value
            
        Returns
        ----------
        S21: 1D-array
            Transmission values for each freq and H values
            
        Example
        ----------
        pos = [[1, 1, 1, 2, 2, 2], [0, 0.1, 0.2, 0, 0.1, 0.2]]
        
        g = float
        
        The function could return:\n\
            slab_model_3D(pos, g) =[-140.278, -130.97, -40.9, -46., -131.2, -143.5]
        """
        
        # Prism dimensions
        a = 0.25
        b = 3
        c = 2
        
        # Ferrimagnetic parameters (default: YIG)
        Ms = 0.176
        gamma = 28
        
        
        np.seterr(all='warn')
        warnings.filterwarnings('error')
            
            
        # Diagonal components of the demagnetizing tensor
        Nzz = 2/(np.pi)*np.arctan(1/self.f_func(a, b, c))
        Nxx = 2/(np.pi)*np.arctan(1/self.f_func(c, b, a))
        Nyy = 2/(np.pi)*np.arctan(1/self.f_func(a, c, b))
            
            
        # Off-diagonal components of the demagnetizing tensor
        Nxy = - 1/(4*np.pi)*np.log((self.G_func(a, b, c)*self.G_func(-a, -b, c)*\
            self.G_func(-a, b, -c)*self.G_func(a, -b, -c))/(self.G_func(-a, b, c)*\
                self.G_func(a, -b, c)*self.G_func(a, b, -c)*self.G_func(a, b, c)))
                
        Nyx = - 1/(4*np.pi)*np.log((self.G_func(b, a, c)*self.G_func(-b, -a, c)*\
            self.G_func(-b, a, -c)*self.G_func(b, -a, -c))/(self.G_func(-b, a, c)*\
                self.G_func(b, -a, c)*self.G_func(b, a, -c)*self.G_func(b, a, c)))
            
            
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
            result[i] = (self.lorentzian(pos[i*self.len_y: (1 + i)*self.len_y, 1], freq_s, self.sigma)+\
            self.lorentzian(pos[i*self.len_y: (1 + i)*self.len_y, 1], freq_i, self.sigma))*(self.S_max - self.S_min) + self.S_min
        
        return np.ravel(result)



    def Slab_model_2D(self, H, g):
        """
        Rectangular prism model
        
        Parameters
        ----------
        H: 1D-array
            Magnetic field values
            
        g: float
            Strentgh coupling value
            
        Returns
        ----------
        freq_s: float
            Superior hybridized frequency
            
        freq_i: float
            Inferior hybridized frequency
            
        freq_FMR: 1D-array:
            Ferromagnetic resonance frequency for each H values
            
        self.freq_c: float
            Cavity frequency
            
        H_cross: float
            H_value at freq_FMR = self.freq_c
        """
        
        # Prism dimensions
        a = 0.25
        b = 3
        c = 2
        
        # Ferrimagnetic parameters (default: YIG)
        Ms = 0.176
        gamma = 28
        
        
        np.seterr(all='warn')
        warnings.filterwarnings('error')
        
                
        # Diagonal components of the demagnetizing tensor
        Nzz = 2/(np.pi)*np.arctan(1/self.f_func(a, b, c))
        Nxx = 2/(np.pi)*np.arctan(1/self.f_func(c, b, a))
        Nyy = 2/(np.pi)*np.arctan(1/self.f_func(a, c, b))
          
        
        # Off-diagonal components of the demagnetizing tensor
        Nxy = - 1/(4*np.pi)*np.log((self.G_func(a, b, c)*self.G_func(-a, -b, c)*\
            self.G_func(-a, b, -c)*self.G_func(a, -b, -c))/(self.G_func(-a, b, c)*\
                self.G_func(a, -b, c)*self.G_func(a, b, -c)*self.G_func(a, b, c)))
                
        Nyx = - 1/(4*np.pi)*np.log((self.G_func(b, a, c)*self.G_func(-b, -a, c)*\
            self.G_func(-b, a, -c)*self.G_func(b, -a, -c))/(self.G_func(-b, a, c)*\
                self.G_func(b, -a, c)*self.G_func(b, a, -c)*self.G_func(b, a, c)))
        
        
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
        delta_cross = ((Nxx - Nyy)**2 + 4*(Nxy + Nyx)**2)*Ms**2 + 4*(self.freq_c/gamma)**2
        H_av = -(Nxx + Nyy)*Ms
                
        H_cross = 0.5*(H_av + np.sqrt(delta_cross))
        
        return freq_s, freq_i, freq_FMR, self.freq_c, H_cross


        
    def Sphere_model_3D(self, pos, g):
        """
        Sphere model
        
        Parameters
        ----------
        pos: 2D-array
            First 1D-array contains frequency values for each H values in the second 1D-array
        
        g: float
            Strentgh coupling value
            
        Returns
        ----------
        S21: 1D-array
            Transmission values for each freq and H values
            
        Example
        ----------
        pos = [[1, 1, 1, 2, 2, 2], [0, 0.1, 0.2, 0, 0.1, 0.2]]
        
        g = float
        
        The function could return:\n\
            sphere_model_3D(pos, g) = [-140.278, -130.97, -40.9, -46., -131.2, -143.5]
        """
        
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
            
            result[i] = (self.lorentzian(pos[i*self.len_y:(1 + i)*self.len_y, 1], freq_s, 0.1)+\
            self.lorentzian(pos[i*self.len_y:(1 + i)*self.len_y, 1], freq_i, 0.1))*(self.S_max - self.S_min) + self.S_min
        
        return np.ravel(result)
        
        
        
    def Sphere_model_2D(self, H, g):
        """
        Sphere model
        
        Parameters
        ----------
        H: 1D-array
            Magnetic field values
            
        g: float
            Strentgh coupling value
            
        Returns
        ----------
        freq_s: float
            Superior hybridized frequency
            
        freq_i: float
            Inferior hybridized frequency
            
        freq_FMR: 1D-array:
            Ferromagnetic resonance frequency for each H values
            
        self.freq_c: float
            Cavity frequency
            
        H_cross: float
            H_value at freq_FMR = self.freq_c
        """
        
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
    
    
    
    def f_func(self, x, y, z):
        """
        Method which uses a function from the rectangular prism model

        Parameters
        ----------
        x, y, z: float
            
        Returns
        ----------
        float
        """
            
        return (np.sqrt(x*x + y*y + z*z)*z)/(x*y)
    
    
    
    def G_func(self, x, y, z):
        """
        Method which uses a function from the rectangular prism model

        Parameters
        ----------
        x, y, z: float
            
        Returns
        ----------
        float
        """
            
        return z + np.sqrt(x*x + y*y + z*z)




if __name__ == '__main__':
    nbp_freq = 3001
    nbp_H = 1401
    
    
    H_file = "D:/Guillaume_B/USC_Que_Choisir/7.5_GHz/H_values.txt"
    freq_file = "D:/Guillaume_B/USC_Que_Choisir/7.5_GHz/f_values.txt"
    S21_file = "D:/Guillaume_B/USC_Que_Choisir/7.5_GHz/S/S12/Intensity.txt"

    
    H_table = np.genfromtxt(H_file, names=True, delimiter = '\n')
    f_table = np.genfromtxt(freq_file, names=True, delimiter = '\n')
    S210 = np.genfromtxt(S21_file, delimiter = ',')
    
    H_name = H_table.dtype.names[0]
    f_name = f_table.dtype.names[0]
    
    H = H_table[H_name]
    f = f_table[f_name]
    
    S21 = np.ravel(S210)
    model = models()
    model.S21_min = min(S21)
    model.search_freq_c(f, [S210[0], S210[int(len(H)/2)]])
    
    
    # Meshgrid for a colormap
    freqg0, Hg0 = np.meshgrid(f, H)
    pos = np.array(list(zip(np.ravel(Hg0), np.ravel(freqg0))))
    

    S21_fit = np.maximum(S21, model.S_min)
    model.len_x = 401
    model.len_y = 3001

    S211 = S21_fit.reshape(model.len_x, model.len_y)
    plt.plot(f, S211[0])
    plt.plot() 

    """
    popt, pcov = scp.curve_fit(model.Slab_model_3D, pos, S21_fit, bounds=(0, 10), maxfev=600)
    popt = popt[0]
    """
    
    fig, ax = plt.subplots()
    im = ax.pcolormesh(Hg0, freqg0, S210, cmap='hot', vmin=-100, vmax = -20, shading='auto')
    ax.set_xlabel('Magnetic Field [T]', fontsize=20)
    ax.set_ylabel('Frequency [GHz]', fontsize=20)
    cb = plt.colorbar(im, ax=ax, boundaries=np.linspace(-140, -20, 100), ticks=np.linspace(-140, -20, 6))
    cb.ax.set_ylabel('S\u2082\u2081 [dB]', rotation=90, size=20, labelpad=10)
    cb.ax.tick_params(labelsize=15) 
    popt = 3
    over2 = model.Slab_model_2D(H, popt)
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