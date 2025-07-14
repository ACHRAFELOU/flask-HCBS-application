import pandas as pd
import matplotlib.pyplot as plt

# Step 2: Read data from Excel file
data = pd.read_excel('T3_2cm.xlsx')

# Step 3: Plot the data
plt.plot(data['X'], data['Height'],  linestyle='-', color='r', label='Profondeur_Minimale')
plt.plot(data['X'], data['Height_2'],  linestyle='-', color='g', label='Profondeur_Maximale')
plt.plot(data['X'], data['Height_3'], linestyle='-', color='b', label='Profondeur_Médium')
plt.plot(data['X'], data['Height_4'], linestyle='--', color='black', label='Absence de tumeur')
plt.xlabel('Longueur de l\'arc du Fantôme mammaire (cm)')
plt.ylabel('Temperature (°C)')
plt.title('Tumor size of 2 cm')

# Set the x-axis and y-axis scales, starting from 0
plt.xticks(range(int(min(data['X'])), int(max(data['X'])) + 1, 1))
plt.yticks([i * 0.05 for i in range(int(min(min(data['Height']), min(data['Height_2']), min(data['Height_3']), min(data['Height_4'])) / 0.05),
                                     int(max(max(data['Height']), max(data['Height_2']), max(data['Height_3']), max(data['Height_4'])) / 0.05) + 1)])
plt.xlim(0, int(max(data['X'])))

plt.grid(True)
plt.legend()
plt.show()
