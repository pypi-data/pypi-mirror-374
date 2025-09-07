import pandas as pd

# Two series
s1 = pd.Series([1, 2, 3])
s2 = pd.Series([4, 5, 6])

print("Series 1:\n", s1)
print("Series 2:\n", s2)

# Stack vertically (like appending)
vertical = pd.concat([s1, s2])
print("\nStacked Vertically:\n", vertical)

# Stack horizontally (side by side as columns)
horizontal = pd.concat([s1, s2], axis=1)
print("\nStacked Horizontally:\n", horizontal)
