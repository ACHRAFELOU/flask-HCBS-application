import matplotlib.pyplot as plt
from tensorflow.keras.utils import plot_model
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, AveragePooling2D, Flatten, Dense, Input

# Define the LeNet-5 model architecture for visualization
model = Sequential([
    Input(shape=(28, 28, 1)),  # Input layer
    Conv2D(filters=6, kernel_size=(5, 5), activation='tanh', padding='same'),  # First Conv Layer
    AveragePooling2D(pool_size=(2, 2)),  # First Pooling Layer
    Conv2D(filters=16, kernel_size=(5, 5), activation='tanh'),  # Second Conv Layer
    AveragePooling2D(pool_size=(2, 2)),  # Second Pooling Layer
    Flatten(),  # Flatten Layer
    Dense(units=120, activation='tanh'),  # First Fully Connected Layer
    Dense(units=84, activation='tanh'),  # Second Fully Connected Layer
    Dense(units=10, activation='softmax')  # Output Layer
])

# Visualize the model architecture
plot_model(model, to_file='/mnt/data/lenet5_architecture.png', show_shapes=True, show_layer_names=True)

# Displaying the generated figure
img = plt.imread('/mnt/data/lenet5_architecture.png')
plt.figure(figsize=(10, 10))
plt.imshow(img)
plt.axis('off')
plt.title("LeNet-5 Architecture")
plt.show()
