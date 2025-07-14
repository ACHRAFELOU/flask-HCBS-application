import pandas as pd
import matplotlib.pyplot as plt

# Step 2: Read data from Excel file
data = pd.read_excel('T1_1cm.xlsx')

# Step 3: Plot the data
plt.plot(data['X'], data['Height'],  linestyle='-', color='r', label='Depth_Min')
plt.plot(data['X'], data['Height_2'],  linestyle='-', color='g', label='Depth_Max')
plt.plot(data['X'], data['Height_3'], linestyle='-', color='b', label='Depth_Medium')
plt.plot(data['X'], data['Height_4'], linestyle='--', color='black', label='No Tumor')
plt.xlabel('Breast Arc Length (cm)')
plt.ylabel('Temperature (°C)')
plt.title('Tumor size of 1 cm')

# Set the x-axis and y-axis scales, starting from 0
plt.xticks(range(int(min(data['X'])), int(max(data['X'])) + 1, 1))
plt.yticks([i * 0.05 for i in range(int(min(min(data['Height']), min(data['Height_2']), min(data['Height_3']), min(data['Height_4'])) / 0.05),
                                     int(max(max(data['Height']), max(data['Height_2']), max(data['Height_3']), max(data['Height_4'])) / 0.05) + 1)])
plt.xlim(0, int(max(data['X'])))

# Display temperature values on the y-axis
plt.gca().get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:.1f}°C".format(x)))

# Add vertical lines for every 0.1°C change
for height_value in plt.yticks()[0]:
    plt.axhline(y=height_value, color='gray', linestyle=':', linewidth=0.5)

# Plot lines where Data2 - Data1 = 0.1°C relative to X2 - X1
for index in range(len(data) - 1):
    if abs(data['Height_2'][index + 1] - data['Height_2'][index] - 0.1) < 0.01:
        plt.plot([data['X'][index], data['X'][index + 1]], [data['Height_2'][index], data['Height_2'][index + 1]], color='blue', linestyle='-', linewidth=0.5)
        plt.plot(data['X'][index], data['Height_2'][index], marker='o', markersize=5, color='blue')
        plt.plot(data['X'][index + 1], data['Height_2'][index + 1], marker='o', markersize=5, color='blue')
        plt.annotate(f'{data["X"][index]:.1f}', (data['X'][index], 0), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=8, color='blue')
        plt.annotate(f'{data["X"][index + 1]:.1f}', (data['X'][index + 1], 0), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=8, color='blue')

plt.xlim(0, int(max(data['X'])))

# Display temperature values on the y-axis
plt.gca().get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:.1f}°C".format(x)))

# Add vertical lines for every 0.1°C change
for height_value in plt.yticks()[0]:
    plt.axhline(y=height_value, color='gray', linestyle=':', linewidth=0.5)

# Find X values where Data2 - Data1 = 0.1°C
x_values = []
for index in range(len(data) - 1):
    if abs(data['Height_2'][index + 1] - data['Height_2'][index] - 0.1) < 0.01:
        x_values.append(data['X'][index + 1] - data['X'][index])

# Plot the X values where Data2 - Data1 = 0.1°C
plt.scatter(x_values, [0.1] * len(x_values), color='blue', marker='o', label='Delta T = 0.1°C')

plt.xlabel('X2 - X1 (cm)')
plt.grid(True)
plt.legend()
plt.show()