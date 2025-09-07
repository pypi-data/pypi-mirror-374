import numpy as np
A=np.arange(1,101).reshape(10,10)

print(A)

print(A[A%2==0])