import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

# Load image
img = Image.open(r'C:\Users\premj\Downloads\MU.jpg')
img_array = np.array(img)

# Extract R, G, B channels
R = img_array[:, :, 0]
G = img_array[:, :, 1]
B = img_array[:, :, 2]

plt.figure(figsize=(12, 4))

# Red channel
plt.subplot(1, 3, 1)
plt.imshow(R, cmap='Reds')
plt.title("Red Channel")
plt.axis("off")

# Green channel
plt.subplot(1, 3, 2)
plt.imshow(G, cmap='Greens')
plt.title("Green Channel")
plt.axis("off")

# Blue channel
plt.subplot(1, 3, 3)
plt.imshow(B, cmap='Blues')
plt.title("Blue Channel")
plt.axis("off")

plt.tight_layout()
plt.show()
