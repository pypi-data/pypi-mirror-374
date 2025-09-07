import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

# Load image
img = Image.open(r'C:\Users\premj\Downloads\MU.jpg')
img_array = np.array(img)

# Add black padding (top=50, bottom=50, left=100, right=100)
padded_img = np.pad(img_array, ((50, 50), (100, 100), (0, 0)), mode='constant', constant_values=0)

# Show original and padded images
plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.imshow(img_array)
plt.title("Original Image")
plt.axis("off")

plt.subplot(1, 2, 2)
plt.imshow(padded_img)
plt.title("Padded Image")
plt.axis("off")

plt.show()
