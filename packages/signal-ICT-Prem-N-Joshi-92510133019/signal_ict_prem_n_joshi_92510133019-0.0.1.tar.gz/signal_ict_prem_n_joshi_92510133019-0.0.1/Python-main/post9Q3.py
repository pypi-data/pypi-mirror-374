import pandas as pd
import numpy as np

# From list
list_data = [10, 20, 30, 40]
s_list = pd.Series(list_data)
print("Series from List:\n", s_list)

# From NumPy array
array_data = np.array([1, 2, 3, 4, 5])
s_array = pd.Series(array_data)
print("\nSeries from NumPy Array:\n", s_array)

# From dictionary
dict_data = {'x': 5, 'y': 10, 'z': 15}
s_dict = pd.Series(dict_data)
print("\nSeries from Dictionary:\n", s_dict)
