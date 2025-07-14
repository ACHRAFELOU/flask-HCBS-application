# Attempting again to create the visualization of the antenna array.

import matplotlib.pyplot as plt
import numpy as np

# Parameters for the 2x2 antenna array
num_elements = 4  # Number of elements (2x2 array)
element_spacing = 0.5  # Spacing between elements in wavelengths
freq = 89e9  # Frequency in Hz
wavelength = 3e8 / freq  # Wavelength in meters

# Coordinates for the 2x2 array
x = np.array([0, 0, element_spacing, element_spacing]) * wavelength
y = np.array([0, element_spacing, 0, element_spacing]) * wavelength

# Plotting the array layout
plt.figure(figsize=(6, 6))
plt.scatter(x, y, c="red", s=150, label="Antenna Elements")

# Annotating the elements
for i in range(len(x)):
    plt.text(x[i], y[i], f"E{i+1}", fontsize=10, ha='center', va='bottom')

# Adding plot details
plt.title("2x2 Microstrip Antenna Array", fontsize=14)
plt.xlabel("X Position (meters)", fontsize=12)
plt.ylabel("Y Position (meters)", fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
plt.axis('equal')
plt.legend()

# Displaying the plot
plt.show()
