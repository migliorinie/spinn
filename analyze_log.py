import numpy as np
import matplotlib.pyplot as plt

handle = open("C_log_test.txt")

arr = np.asarray([float(i) for i in handle.readline().split(" ")[:-1]])
plt.plot(arr)
plt.show()