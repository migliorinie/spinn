import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as opt
import sys

# Sadly, there isn't a better way to write a sum of sinusoids
def func(x, a0, a1, b1, a2, b2, a3, b3, a4, b4, a5, b5, a6, b6, a7, b7, a8, b8, a9, b9, a10, b10):
    return a0 + a1*np.cos((x/1000)*2*np.pi*1) + b1*np.sin((x/1000)*2*np.pi*1) + a2*np.cos((x/1000)*2*np.pi*2) + b2*np.sin((x/1000)*2*np.pi*2) + a3*np.cos((x/1000)*2*np.pi*3) + b3*np.sin((x/1000)*2*np.pi*3) + a4*np.cos((x/1000)*2*np.pi*4) + b4*np.sin((x/1000)*2*np.pi*4) + a5*np.cos((x/1000)*2*np.pi*5) + b5*np.sin((x/1000)*2*np.pi*5) + a6*np.cos((x/1000)*2*np.pi*6) + b6*np.sin((x/1000)*2*np.pi*6) + a7*np.cos((x/1000)*2*np.pi*7) + b7*np.sin((x/1000)*2*np.pi*7) + a8*np.cos((x/1000)*2*np.pi*8) + b8*np.sin((x/1000)*2*np.pi*8) + a9*np.cos((x/1000)*2*np.pi*9) + b9*np.sin((x/1000)*2*np.pi*9) + a10*np.cos((x/1000)*2*np.pi*10) + b10*np.sin((x/1000)*2*np.pi*10)

handle = open(sys.argv[1])

x_arr = np.linspace(0, 1000, 1000)
y_arr = np.asarray([float(i) for i in handle.readline().split(" ")[:-1]])

popt, popcv = opt.curve_fit(func, x_arr, y_arr)

# Overfitting yay!
prarr = [popt[0] + popt[1]*np.cos((x/1000)*2*np.pi*1) + popt[2]*np.sin((x/1000)*2*np.pi*1) + popt[3]*np.cos((x/1000)*2*np.pi*2) + popt[4]*np.sin((x/1000)*2*np.pi*2) + popt[5]*np.cos((x/1000)*2*np.pi*3) + popt[6]*np.sin((x/1000)*2*np.pi*3) + popt[7]*np.cos((x/1000)*2*np.pi*4) + popt[8]*np.sin((x/1000)*2*np.pi*4) + popt[9]*np.cos((x/1000)*2*np.pi*5) + popt[10]*np.sin((x/1000)*2*np.pi*5) + popt[11]*np.cos((x/1000)*2*np.pi*6) + popt[12]*np.sin((x/1000)*2*np.pi*6) + popt[13]*np.cos((x/1000)*2*np.pi*7) + popt[14]*np.sin((x/1000)*2*np.pi*7) + popt[15]*np.cos((x/1000)*2*np.pi*8) + popt[16]*np.sin((x/1000)*2*np.pi*8) + popt[17]*np.cos((x/1000)*2*np.pi*9) + popt[18]*np.sin((x/1000)*2*np.pi*9) + popt[19]*np.cos((x/1000)*2*np.pi*10) + popt[20]*np.sin((x/1000)*2*np.pi*10) for x in x_arr]

plt.plot(prarr)
plt.plot(y_arr)
plt.show()