# Given a path to a measurement folder, plot the S parameters of interest

import matplotlib as mpl
import matplotlib.pyplot as plt
from cmcrameri import cm

# colourmap = cm.imola    # Yellow max, green, blue min
# colourmap = cm.lajolla_r  # Yellow max, red, black min.
colourmap = cm.oslo  # White max, blue, black min

import numpy as np
from numpy import abs, max, pi
import pickle


def index_of_nearest(array, value):
    return (np.abs(array - value)).argmin()


class Measurement:
    def __init__(self, measurement_folder):
        self.path = measurement_folder

        self.f = np.genfromtxt(self.path + "/f_values.txt", delimiter='\n', skip_header=1)
        self.H = np.genfromtxt(self.path + "/H_values.txt", delimiter='\n', skip_header=1)

        S_param_delimiter = r','
        self.S21 = np.genfromtxt(self.path + "/S/S21/Magnitude.txt", delimiter=S_param_delimiter, skip_header=1).transpose()
        self.S21_phase = np.genfromtxt(self.path + "/S/S21/Phase.txt", delimiter=S_param_delimiter, skip_header=1).transpose()

    def pickle(self):
        """
        Convert to a numpy-compatible file format
        Note that this must be called from outside this script to work
        See https://www.pythonanywhere.com/forums/topic/27818/#id_post_81907
        """
        with open(self.path + "measurement.pkl", "wb") as file:
            pickle.dump({
                "frequency": self.f,
                "magnetic_field": self.H,
                "S21_amplitude": self.S21,
                "S21_phase": self.S21_phase
            }, file)
    
    def display(self, show=True, H_lim=None, freq_lim=None, phase=False, diff=False, diff_max=None, colormap=cm.grayC,
                fig=None, ax=None):
        """
        Display the data in the specified range.
        :return: fig, ax
        """
        magnetic_field, frequency, S21, S21_phase = self.H, self.f, self.S21, self.S21_phase

        if H_lim is not None:
            indices = index_of_nearest(magnetic_field, H_lim[0]), index_of_nearest(magnetic_field, H_lim[1])
            magnetic_field = magnetic_field[indices[0]:indices[1]+1]
            S21 = S21[:, indices[0]:indices[1]+1]
            S21_phase = S21_phase[:, indices[0]:indices[1]+1]

        if freq_lim is not None:
            indices = index_of_nearest(frequency, freq_lim[0]), index_of_nearest(frequency, freq_lim[1])
            frequency = frequency[indices[0]:indices[1]+1]
            S21 = S21[indices[0]:indices[1]+1, :]
            S21_phase = S21_phase[indices[0]:indices[1]+1, :]
        if diff:
            S21 = np.abs(np.diff(S21) / np.diff(self.H))
            S21_phase = np.diff(S21_phase)

        if not phase:
            if diff:
                if diff_max is None:
                    diff_max = max(abs(S21))
                fig, ax = self.input_output_plot(magnetic_field[:-1] * 1e3, frequency, S21, fig=fig, ax=ax,
                                            dB=False,
                                            colorbar_lims=[0, diff_max], colormap=colormap,
                                            colorbar_format='%.0f', colorbar_label="$d|S_{21}|/dH$")
            else:
                fig, ax = self.input_output_plot(magnetic_field*1e3, frequency, S21, fig=fig, ax=ax, dB=True, dB_step=20,
                                            colorbar_format='%.0f')
        else:
            fig, ax = self.input_output_plot(magnetic_field*1e3, frequency, S21_phase, fig=fig, ax=ax, dB=True, dB_step=20,
                                        colorbar_format='%.0f', colorbar_label="arg $S_{21}$ (degrees)")
        ax.set_xlabel("Applied magnetic field (mT)")
        fig.suptitle(self.name + " data")
        fig.tight_layout()

        if show:
            plt.show()

        return fig, ax

    @staticmethod
    def input_output_plot(x, y, s_param, fig=None, ax=None, show=False, colorbar_label=None, dB=False, dB_step=10,
                      colorbar_lims=None, colorbar_ticks=None, colorbar_format='%0.1f', colormap=colourmap):
        if (fig is None) or (ax is None):
            fig, ax = plt.subplots(1, 1)

        ax.grid(False)
        if colorbar_lims is None:
            if not dB:
                colorbar_lims = (0, 1)
            else:
                colorbar_lims = (np.min(s_param), np.max(s_param))
        c = ax.pcolormesh(x, y, s_param, shading='auto',
                        vmin=colorbar_lims[0], vmax=colorbar_lims[1], cmap=colormap)

        ax.set_xlim(x[0], x[-1])
        ax.set_ylim(y[0], y[-1])
        ax.set_xlabel(r"Matter mode(s) frequency $\omega_b/(2\pi)$ (GHz)")
        ax.set_ylabel(r"Frequency $\omega/(2\pi)$ (GHz)")

        if colorbar_label is None:
            if not dB:
                colorbar_label = "$|S_{21}|$"
            else:
                colorbar_label = "$|S_{21}|$ (dB)"

        ax.grid(False)
        if (colorbar_ticks is None) and (dB is not None) and dB:
            # Smart colorbar ticks: display min and max, but round uniformly between
            a, b = round(colorbar_lims[0], -1), round(colorbar_lims[1], -1)
            colorbar_ticks = np.arange(a, b+dB_step, dB_step)
            if colorbar_lims[0] not in colorbar_ticks:
                colorbar_ticks = np.append(np.array([colorbar_lims[0]]), colorbar_ticks)
            if colorbar_lims[1] not in colorbar_ticks:
                colorbar_ticks = np.append(colorbar_ticks, np.array([colorbar_lims[1]]))
        fig.colorbar(c, ax=ax, label=colorbar_label, pad=0.05, ticks=colorbar_ticks)

        fig.tight_layout()

        if show:
            plt.show()

        return fig, ax

    def trim_frequency_range(self, f_lims):
        f_min_idx, f_max_idx = index_of_nearest(self.f, f_lims[0]), index_of_nearest(self.f, f_lims[1])
        return self.f[f_min_idx:f_max_idx+1], self.S21[f_min_idx:f_max_idx+1, :]

    def plot_slice(self, H_applied, f_lims=None):
        fig, ax = plt.subplots(1, 1)

        if f_lims is None:
            ax.plot(self.f, self.S21[:, index_of_nearest(self.H, H_applied)])
        else:
            f_min_idx, f_max_idx = index_of_nearest(self.f, f_lims[0]), index_of_nearest(self.f, f_lims[1])
            ax.plot(self.f[f_min_idx:f_max_idx+1], self.S21[f_min_idx:f_max_idx+1, index_of_nearest(self.H, H_applied)])

            res = self.find_resonance(self.f[f_min_idx:f_max_idx+1]/1e9, self.S21[f_min_idx:f_max_idx+1, index_of_nearest(self.H, H_applied)])
            print(res.frequency_GHz)
        ax.set_xlabel("Frequency (GHz)")
        ax.set_ylabel("$|S_{21}|$ (dB)")
        fig.suptitle("Slice at $H=%0.3f$ mT" % H_applied)
        plt.show()

    class Resonance:
        def __init__(self, frequency, quality_factor, amplitude, bandwidth):
            self.frequency = frequency
            self.frequency_GHz = frequency / 1e9
            self.quality_factor = quality_factor
            self.amplitude = amplitude
            self.bandwidth = bandwidth

        def __str__(self):
            return "f=%0.3f GHz, Q=%0.2f" % (self.frequency_GHz, self.quality_factor)
    
    def find_resonance(self, f, S):
        """
        From the given numerical data, return the amplitude of the peak, the resonance frequency, the 3dB bandwidth,
        and the quality factor.
        Make sure the given range contains a peak!
        :param f: frequency in Hz
        :param S: S parameter in dB
        :return:
        """
        if len(f) != len(S):
            raise ValueError("Frequency and S parameter of different lengths!")

        A_max = np.max(S)
        f0_idx = np.argmax(S)
        f0 = f[f0_idx]

        A_bandwidth = A_max - 3
        diff = np.abs(S - A_bandwidth)
        bandwidth_bound_1 = np.argmin(diff)
        diff[bandwidth_bound_1] = np.Inf
        bandwidth_bound_2 = np.argmin(diff)
        bandwidth = np.abs(f[bandwidth_bound_1] - f[bandwidth_bound_2])
        Q = f0 / bandwidth

        return self.Resonance(f0, Q, A_max, bandwidth)



if __name__ == "__main__":
    mpl.rcParams['font.size'] = 12
    mpl.rcParams['xtick.labelsize'] = 15
    mpl.rcParams['ytick.labelsize'] = 15
    mpl.rcParams['lines.linewidth'] = 2.5
    mpl.rcParams['lines.markersize'] = 2.5
    mpl.rcParams['axes.grid'] = False
    mpl.rcParams['figure.dpi'] = 300
    mpl.rcParams['figure.figsize'] = [8, 6]
    plt.rcParams['axes.xmargin'] = 0
    plt.rcParams['axes.ymargin'] = 0

    # measurement = Measurement(measurement_folder=r"D:\\Measures\\Alan\\coupling-phase-cavity\\1.yig1_left_yig2_right_2GHz-10GHz\\")
    measurement = Measurement(measurement_folder=r"D:\\Measures\\Alan\\thor-cavity\\2.9GHz-16GHz_yig1-rhom-up_yig_2-rhom-down_fast\\")
    