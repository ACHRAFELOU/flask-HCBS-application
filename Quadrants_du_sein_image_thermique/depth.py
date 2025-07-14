import pandas as pd
import matplotlib.pyplot as plt

# Step 2: Read data from Excel file
data = pd.read_excel('C:/Users/a.elouerghi/PycharmProjects/Dmin.xlsx')

# Step 3: Plot the data
plt.plot(data['X'], data['Height'],  linestyle='-', color='k')
plt.xlabel('Breast Arc Length (cm)')
plt.ylabel('Temperature (°C)')
plt.title('Tumor size of 2 cm')

# Set the x-axis and y-axis scales, starting from 0
plt.xticks(range(int(min(data['X'])), int(max(data['X'])) + 1, 1))
min_height = min(data['Height'])
max_height = max(data['Height'])

plt.yticks([i * 0.05 for i in range(int(min_height / 0.05), int(max_height / 0.05) + 1)])

plt.xlim(0, int(max(data['X'])))
plt.grid(True)
plt.show()
