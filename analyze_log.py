import numpy as np
import matplotlib.pyplot as plt

import scipy.fftpack as fft
from scipy.stats.stats import pearsonr

import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('file', metavar='file', type=str, help='the file to analyze')
#parser.add_argument('-o', dest='output', help='the output file')
parser.add_argument('-c', dest='comparison', type=str, help='the file to compare')
parser.add_argument('-d', dest='display', action='store_true', help='graphically display the results')
parser.add_argument('--plots', dest='plots', action='store_true', help='display the original arrays')

args = parser.parse_args()

cutoff = 50
   
try:
    handle = open(args.file)

    y_arr = np.asarray([float(i) for i in handle.readline().split(" ")[:-1]])

    fourarr = fft.rfft(y_arr)
    selarr = [0 for i in fourarr]
    selarr[:cutoff] = fourarr[:cutoff]
    adarr = fft.irfft(selarr)
except FileNotFoundError as e:
    print("Invalid input file!")

if args.comparison is not None:
    try:
        chandle = open(args.comparison)
        cy_arr = np.asarray([float(i) for i in chandle.readline().split(" ")[:-1]])

        cfourarr = fft.rfft(cy_arr)
        cselarr = [0 for i in cfourarr]
        cselarr[:cutoff] = cfourarr[:cutoff]
        cadarr = fft.irfft(cselarr)
        
        print("Pearson's correlation coefficient for the reconstructions:")
        print("----------------------------------")
        print(pearsonr(adarr, cadarr))
        print("Pearson's correlation coefficient for the coefficients:")
        print("----------------------------------")
        print(pearsonr(selarr[:cutoff], cselarr[:cutoff]))
    except FileNotFoundError as e:
        print("Invalid comparison file!")

#plt.plot(fourarr, "b")
#plt.plot(selarr, "r")

if args.plots and args.comparison:
    plt.plot(y_arr, "b")
    plt.plot(cy_arr, "r")
    plt.show()

if args.display:
    if args.comparison is None:
        plt.plot(y_arr, "b")
        plt.plot(adarr, "r")
        plt.show()
    else:
        plt.plot(adarr, "b")
        plt.plot(cadarr, "r")
        plt.show()
