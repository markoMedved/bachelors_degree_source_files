import matplotlib.pyplot as plt
from nptdms import TdmsFile
from datetime import date
import math
import numpy as np
import scipy
import scipy.integrate
from scipy.signal import  butter, freqz, lfilter



#def butter_lowpass(cutoff, fs, order=5):
    #return firwin(order, cutoff,fs=fs)

def butter_lowpass(cutoff, fs, order=5):
    nyquist = 0.5 * fs  # Nyquist frequency
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y



path =""


#read tdms file
with TdmsFile.open(path) as file:
    #all data
    data = file["DATA"] 
    #absolute acceleration array, odvisno kere poskuse gledaš
    F1 =   data["Force z1"][:] +  data["Force z2"][:]
    Fx = data["Force y1"][:]
    #F2 = data["Force z2"][:]
    acc1 = data["empty"][:]
    acc2= 100* data["empty1"][:]

    accVert = data["LAx3"][:]
    time = data["LV Ts"][:]


avg = np.average(F1[0:300])
print(np.average(F1[0:300]))
F1 -= avg
F1 /= avg*9.81



#set time to run from 0
time[:] = time[:] - time[0]
#modify time to seconds
time = time / 1000

samples = []
for i in range(0, len(F1)):
    samples.append(i)



#accVert = butter_lowpass_filter(accVert, 15, 100)

v = [0]

for i in range(1, len(accVert)):
    v.append(v[i-i] + accVert[i]*9.81* 0.005)

z = [0]

for i in range(1, len(v)):
    z.append(z[i-i] + (v[i] + v[i-1])/2* 0.005)

plt.plot(time,acc1, label='y[t]')
#plt.plot(time,accVert, color='r', label='jerk')
#plt.plot(time,acc2)

#plt.ylim(-40,2500)


plt.xlabel("čas [s]",fontsize=15)
plt.ylabel("Sila [N]",fontsize=15)


plt.show()



