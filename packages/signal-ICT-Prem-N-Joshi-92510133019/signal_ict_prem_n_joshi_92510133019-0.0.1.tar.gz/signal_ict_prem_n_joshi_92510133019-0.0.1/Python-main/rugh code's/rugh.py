# # # # import pandas as pd
# # # # # Creating a Series
# # # # # Creating a DataFrame
# # # # data = {
# # # #     'Name': ['Alice', 'Bob', 'Charlie'],
# # # #     'Age': [25, 30, 35],
# # # #     'City': ['New York', 'Los Angeles', 'Chicago']
# # # # }
# # # # df = pd.DataFrame(data)


# # # # # # Accessing Columns (# select one column)
# # # # # print(df[['Name']])

# # # # # df['Salary'] = [70000, 80000, 90000]
# # # # # print(df)

# # # # # Dropping a Column
# # # # # df = df.drop('City', axis=1)
# # # # # print(df)

# # # # # # Return row 0:
# # # # # print(df.loc[[0]])

# # # # #Return row 0 and 1:
# # # # #use a list of indexes:
# # # # print(df.loc[[0, 1]])
# # # import pandas as pd
# # # data = {
# # #   "calories": [420, 380, 390],
# # #   "duration": [50, 40, 45]
# # # }
# # # # df = pd.DataFrame(data, index = ["day1", "day2", "day3"])
# # # # print(df)
# # # # dat = pd.read_csv("data.csv")
# # # # print(dat)
# # # Biodata = {'Name': ['John', 'Emily', 'Mike', 'Lisa'],
# # #         'Age': [28, 23, 35, 31],
# # #         'Gender': ['M', 'F', 'M', 'F']
# # #         }
# # # df = pd.DataFrame(Biodata)
# # # # Save the dataframe to a CSV file
# # # df.to_csv('Biodata.csv', index=False)

# # import pandas as pd

# # # # Create a dictionary
# # # Biodata = {
# # #     'Name': ['John', 'Emily', 'Mike', 'Lisa'],
# # #     'Age': [28, 23, 35, 31],
# # #     'Gender': ['M', 'F', 'M', 'F']
# # # }

# # # # Convert dictionary to DataFrame
# # # df = pd.DataFrame(Biodata)

# # # # Save the DataFrame to a CSV file
# # # df.to_csv('Biodata.csv', index=False)

# # # print("DataFrame has been written to Biodata.csv")

# # dat = pd.read_csv("data.csv")
# # print(dat.info())
# # # shows first and last five rows
# # # print(dat.head())
# # # print(dat.tail())
# # # print(dat.describe())
# # # print(dat[['Name']])
# # # print(dat[['Name','Number']])
# # # print(dat.loc[[1]])
# # dat['A'] = dat['A'] * 2 # Modify a column.
# # dat['F'] = dat['A'] + dat['B'] #Create a new column based on existing columns.
# # dat.drop(columns=['A']) #Drop a column.
# # dat.drop(index=[0]) #Drop a row.

# import pandas as pd
# import numpy as np

# data = {
#     'A': [np.nan, 2, 3, 4, 5, 6, 7, 8, 9, 10],
#     'B': np.random.normal(50, 15, 10),
#     'C': np.random.rand(10) * 100,
#     'D': np.linspace(1, 10, 10),
#     'E': np.logspace(1, 2, 10)
# }
# df = pd.DataFrame(data)
# print(data)


# # Create a sample DataFrame
# # dat = pd.DataFrame({
# #     'A': [1, 2, 3, 4],
# #     'B': [10, 20, 30, 40],
# #     'C': ['x', 'y', 'z', 'w']
# # })

# # print("Original DataFrame:")
# # print(dat)

# # # 1. Modify a column (double the values of column A)
# # dat['A'] = dat['A'] * 2
# # print("\nAfter modifying column A (A * 2):")
# # print(dat)

# # # 2. Create a new column based on existing columns
# # dat['F'] = dat['A'] + dat['B']
# # print("\nAfter creating new column F = A + B:")
# # print(dat)

# # # 3. Drop a column (remove column A)
# # dat_drop_col = dat.drop(columns=['A'])
# # print("\nAfter dropping column A:")
# # print(dat_drop_col)

# # # 4. Drop a row (remove row with index 0)
# # dat_drop_row = dat.drop(index=[0])
# # print("\nAfter dropping row with index 0:")
# # print(dat_drop_row)
