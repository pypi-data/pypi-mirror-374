#Create a 4×4 NumPy matrix with values from 1 to 16. Extract the first two rows.

import numpy as np
A=np.arange(1,17).reshape(4,4)

print(A)

print(A[0:2])