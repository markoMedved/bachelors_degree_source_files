import matplotlib.pyplot as plt
from nptdms import TdmsFile
from datetime import date
import math
import numpy as np
import scipy.signal
import scipy.integrate

path =""


def butter_lowpass(cutoff, fs, order=5):
    nyquist = 0.5 * fs  # Nyquist frequency
    normal_cutoff = cutoff / nyquist
    b, a = scipy.signal.butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = scipy.signal.lfilter(b, a, data)
    return y



#read tdms file
with TdmsFile.open(path) as file:
    #all data
    data = file["DATA"] 
    acc1 = 100* data["empty"][:]
    acc2= 100* data["empty1"][:]

    accVert = data["LAx3"][:]
    time = data["LV Ts"][:]

#accVert = butter_lowpass_filter(accVert, 15, 100)

v = 0

for i in range(875, 972):
    v += accVert[i]*9.81* 0.005

print(v)
