from . su
from PIL import Image
import matplotlib.pyplot as plt

# Load Image
img = Image.open(r'C:\Users\premj\Downloads\MU.jpg')
img_array = np.array(img)

# Display details
print("Image Dimensions (H, W, C):", img_array.shape)
print("Shape of Image:", img_array.shape)

# Minimum pixel value in Blue channel
min_pixel_B = img_array[:,:,2].min()
print("Minimum Pixel Value in Blue Channel:", min_pixel_B)

# Show image using imshow
plt.imshow(img_array)
plt.title("Original Image")
plt.axis("off")
plt.show()
