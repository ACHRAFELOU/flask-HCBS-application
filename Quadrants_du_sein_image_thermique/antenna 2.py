# Final attempt to visualize and save the 2x2 microstrip antenna array layout.

import matplotlib.pyplot as plt
import numpy as np

# Parameters for the antenna array
element_spacing = 0.5  # Spacing between elements in wavelengths
freq = 89e9  # Frequency in Hz
wavelength = 3e8 / freq  # Wavelength in meters

# Coordinates for the 2x2 array (normalized to wavelength)
x = np.array([0, 0, element_spacing, element_spacing]) * wavelength
y = np.array([0, element_spacing, 0, element_spacing]) * wavelength

# Plotting the antenna layout
plt.figure(figsize=(6, 6))
plt.scatter(x, y, color="red", s=150, label="Antenna Elements")

# Adding labels to each element
for i in range(len(x)):
    plt.text(x[i], y[i], f"E{i+1}", fontsize=10, ha="center", va="bottom")

# Adding grid, labels, and title
plt.grid(True, linestyle="--", alpha=0.7)
plt.title("2x2 Microstrip Antenna Array Layout", fontsize=14)
plt.xlabel("X Position (meters)", fontsize=12)
plt.ylabel("Y Position (meters)", fontsize=12)
plt.axis("equal")
plt.legend()

# Save the plot to a file
output_path = "C:/Users/a.elouerghi/Desktop/Article-2025/antenna_array_layout.png"
plt.savefig(output_path)
plt.show()

# Provide the saved file path
output_path
