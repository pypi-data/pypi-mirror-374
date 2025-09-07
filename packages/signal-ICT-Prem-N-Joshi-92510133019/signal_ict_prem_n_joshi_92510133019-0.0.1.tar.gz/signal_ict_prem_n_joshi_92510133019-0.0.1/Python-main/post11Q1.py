import numpy as np
from PIL import Image

# Load the image
img = Image.open(r'C:\Users\premj\Downloads\MU.jpg')
img_array = np.array(img)

# Display details
print("Dimension of image:", img_array.ndim)     
print("Shape of image:", img_array.shape)        
print("Minimum pixel value at channel B:", img_array[:, :, 2].min())