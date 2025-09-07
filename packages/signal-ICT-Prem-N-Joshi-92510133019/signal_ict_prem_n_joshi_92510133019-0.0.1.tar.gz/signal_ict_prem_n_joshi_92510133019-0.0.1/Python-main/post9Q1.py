import pandas as pd

# Create two series
s1 = pd.Series([10, 20, 30, 40])
s2 = pd.Series([1, 2, 3, 4])

print("Series 1:\n", s1)
print("Series 2:\n", s2)

# Arithmetic operations
print("\nAddition:\n", s1 + s2)
print("\nSubtraction:\n", s1 - s2)
print("\nMultiplication:\n", s1 * s2)
print("\nDivision:\n", s1 / s2)
    