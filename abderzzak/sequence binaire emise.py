import numpy as np
from scipy.signal import butter, lfilter
import matplotlib.pyplot as plt

# Génération de la séquence binaire
def generate_binary_sequence(length):
    return np.random.randint(0, 2, length)

# Codage en ligne NRZ
def encode_line(sequence):
    return np.where(sequence == 0, -1, 1)

# Filtre passe-bas
def lowpass_filter(signal, cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = lfilter(b, a, signal)
    return y

# Modulation BPSK
def bpsk_modulation(encoded_signal):
    return np.cos(np.pi * encoded_signal)

# Canal de propagation avec bruit gaussien
def add_noise(signal, snr):
    signal_power = np.mean(signal**2)
    noise_power = signal_power / (10**(snr / 10))
    noise = np.sqrt(noise_power) * np.random.randn(len(signal))
    return signal + noise

# Démodulation BPSK
def bpsk_demodulation(received_signal):
    return np.cos(np.pi * received_signal)

# Prise de décision
def decision(signal):
    return np.where(signal >= 0, 1, 0)
