import pandas as pd
print(pd.__version__)
data = [1, 2, 3, 4, 5]
series = pd.Series(data)
print(series)
series2 = series + 10
print(series2)

filtered_series = series[series > 2]
print(filtered_series)

mean_value = series.mean()
print(mean_value)

data = {
'Name': ['Alice', 'Bob', 'Charlie'],
'Age': [25, 30, 35],
'City': ['New York', 'Los Angeles', 'Chicago']
}
df = pd.DataFrame(data)
print(df)

print(df[['Name']])
print(df[['Name','City']])

df['Salary'] = [70000, 80000, 90000]
print(df)

df = df.drop('City', axis=1)
print(df)

print(df.loc[[0]])
print(df.loc[[0,1]])
print(df.loc[[0,2]])

# Return row 0:
print(df.loc[[0]])



data = {
"calories": [420, 380, 390],
"duration": [50, 40, 45]
}
df = pd.DataFrame(data, index = ["day1", "day2", "day3"])
print(df)   


dat = pd.read_csv("E:\MU\PWP\PWP MS\data.csv")
print(dat)


Biodata = {'Name': ['John', 'Emily', 'Mike', 'Lisa'],
'Age': [28, 23, 35, 31],
'Gender': ['M', 'F', 'M', 'F']
}
df = pd.DataFrame(Biodata)
# Save the dataframe to a CSV file
df.to_csv('Biodata.csv', index=False)


dat = pd.read_csv("E:\MU\PWP\PWP MS\data.csv")
print(dat.info())
# shows first and last five rows
print(dat.head())
print(dat.tail())
print(dat.describe())


print(dat[['Name']])
print(dat[['Name','Number']])
print(dat.loc[[1]])

# Create a DataFrame with 5 numeric columns
data = {
    'A': [pd.nan, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'B': pd.random.normal(50, 15, 10),
    'C': pd.random.rand(10) * 100,
    'D': pd.linspace(1, 10, 10),
    'E': pd.logspace(1, 2, 10)
}
df = pd.DataFrame(data)




# *************************************************************
# postlab 1
import pandas as pd

s1 = pd.Series([10, 20, 30, 40, 50])
s2 = pd.Series([2, 4, 6, 8, 10])

print("Series 1:")
print(s1)
print("\nSeries 2:")
print(s2)

print("\nAddition of two Series:")
print(s1 + s2)

print("\nSubtraction of two Series:")
print(s1 - s2)

print("\nMultiplication of two Series:")
print(s1 * s2)

print("\nDivision of two Series:")
print(s1 / s2)

