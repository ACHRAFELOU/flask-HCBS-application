import numpy as np
from scipy.signal import butter, lfilter
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, messagebox
import wave
import sounddevice as sd

class AdaptiveFilter:
    def __init__(self, order, step_size):
        self.order = order
        self.step_size = step_size
        self.weights = np.zeros(order)

    def update(self, input_signal, desired_signal):
        input_signal = np.pad(input_signal, (self.order-1, 0), mode='constant')
        error = desired_signal - np.convolve(input_signal, self.weights, mode='valid')
        update_term = self.step_size * np.convolve(input_signal, error, mode='valid')
        self.weights += update_term
        print("Weights:", self.weights)
        return error

class DigitalTransmissionApp:
    def __init__(self, master):
        self.master = master
        master.title("Chaîne de Transmission Numérique")

        self.label = tk.Label(master, text="Choisir un fichier audio WAV:")
        self.label.pack()

        self.load_button = tk.Button(master, text="Charger Audio", command=self.load_audio)
        self.load_button.pack()

        self.transmission_button = tk.Button(master, text="Exécuter Transmission", command=self.run_transmission)
        self.transmission_button.pack()

        self.reception_button = tk.Button(master, text="Exécuter Réception", command=self.run_reception)
        self.reception_button.pack()

        self.result_label = tk.Label(master, text="")
        self.result_label.pack()

        self.audio_data = None
        self.samplerate = None
        self.transmitted_signal = None

    def load_audio(self):
        try:
            file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
            if file_path:
                self.wave_file = wave.open(file_path, 'r')
                num_frames = self.wave_file.getnframes()
                self.audio_data = np.frombuffer(self.wave_file.readframes(num_frames), dtype=np.int16)
                self.samplerate = self.wave_file.getframerate()
                messagebox.showinfo("Info", "Fichier audio chargé avec succès")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement du fichier audio: {str(e)}")

    def audio_to_binary(self, audio_data, threshold):
        binary_sequence = np.where(audio_data > threshold, 1, 0)
        return binary_sequence

    def play_audio(self, audio_data, samplerate):
        audio_data = audio_data / np.max(np.abs(audio_data))
        audio_data = audio_data.astype(np.float32)
        sd.play(audio_data, samplerate=samplerate)
        sd.wait()

    def plot_signal(self, signal, title, ylabel):
        plt.figure()
        plt.plot(signal)
        plt.title(title)
        plt.xlabel('Échantillons')
        plt.ylabel(ylabel)
        plt.grid(True)
        plt.show()

    def run_transmission(self):
        try:
            if self.audio_data is None:
                messagebox.showerror("Erreur", "Aucun fichier audio chargé")
                return

            # Convertir les échantillons audio en séquence binaire
            binary_sequence = self.audio_to_binary(self.audio_data, threshold=0)
            encoded_sequence = np.where(binary_sequence == 0, -1, 1)
            filtered_emission = lfilter(*butter(20, 0.35, 'low', analog=False), encoded_sequence)
            modulated_signal = np.cos(np.pi * filtered_emission)

            # Ajout de bruit
            signal_power = np.mean(modulated_signal ** 2)
            noise = np.random.normal(0, np.sqrt(signal_power / (10 ** (10 / 10))), len(modulated_signal))
            noisy_signal = modulated_signal + noise

            # Sauvegarde du signal bruité pour la réception
            self.transmitted_signal = noisy_signal

            # Lecture et tracé des signaux
            self.plot_signal(self.audio_data, 'Audio Original', 'Amplitude')
            self.play_audio(self.audio_data, self.samplerate)  # Fichier audio chargé

            self.plot_signal(noisy_signal, 'Signal Bruité', 'Amplitude')
            self.play_audio(noisy_signal, self.samplerate)  # Signal bruité

            # Affichage des résultats
            self.result_label.config(text="Transmission terminée")

        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur s'est produite lors de la transmission: {str(e)}")

    def run_reception(self):
        try:
            if self.transmitted_signal is None:
                messagebox.showerror("Erreur", "Aucun signal transmis")
                return

            # Ajout d'un délai pour laisser le temps au système de se stabiliser
            sd.sleep(int(len(self.transmitted_signal) / self.samplerate * 1000))

            # Démodulation du signal reçu
            demodulated_signal = np.sign(self.transmitted_signal)

            # Filtrage adaptatif du signal reçu
            adaptive_filter = AdaptiveFilter(order=1000, step_size=0.1)  # Ajuster les paramètres ici
            filtered_reception = adaptive_filter.update(demodulated_signal, np.zeros_like(demodulated_signal))

            # Affichage des résultats
            self.plot_signal(demodulated_signal, 'Signal Démodulé', 'Amplitude')
            self.play_audio(demodulated_signal, self.samplerate)  # Signal démodulé

            self.plot_signal(filtered_reception, 'Signal Réception Filtré', 'Amplitude')
            self.play_audio(filtered_reception, self.samplerate)  # Signal réception filtré

            self.result_label.config(text="Réception terminée")

        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur s'est produite lors de la réception: {str(e)}")

root = tk.Tk()
app = DigitalTransmissionApp(root)
root.mainloop()
