import matplotlib.pyplot as plt

x = [1, 2, 3, 4, 5]
y1 = [1, 2, 3, 4, 5]
y2 = [1, 4, 9, 16, 25]
y3 = [1, 8, 27, 64, 125]

plt.plot(x, y1, label="y = x")
plt.plot(x, y2, label="y = x²")
plt.plot(x, y3, label="y = x³")

plt.xlabel("X Axis")
plt.ylabel("Y Axis")
plt.title("Multiple Line Plot")
plt.legend()

plt.show()


