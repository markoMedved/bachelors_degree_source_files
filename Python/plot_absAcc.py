import matplotlib.pyplot as plt
from nptdms import TdmsFile
from datetime import date
import math
import numpy as np
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
    acc = data["Ax1"][:]
    #force = data["Force z1"][:] + data["Force z2"]

    #x  = data["QTM X1"][:]
    #y = data["QTM Y1"][:]
    #z = data["QTM Z1"][:]
    #time array
    time = data["LV Ts"][:]

#ymin = 70
#y -= ymin


fs = 200
cuttoff = 15
oreder = 10

#y = butter_lowpass_filter(y,cuttoff, fs, order=oreder)
#x = butter_lowpass_filter(x,cuttoff, fs, order=oreder)
#z = butter_lowpass_filter(z,cuttoff, fs, order=oreder)
#acc = butter_lowpass_filter(acc, cuttoff, fs, order=oreder)

#y[:len(y) - oreder] = y[oreder: len(y)]
#x[:len(y) - oreder] = x[oreder: len(y)]
#z[:len(y) - oreder] = z[oreder: len(y)]


vx = [0]
vy = [0]
vz = [0]

ay = [0]
ax = [0]
az = [0]
a = [0]

#corr = 0
#amoc = 0
#accmoc = 0

"""""
for i in range(0, len(x)-1):
    vy.append((y[i+1] - y[i])/5)
    vx.append((x[i+1] - x[i])/5)
    vz.append((z[i+1] - z[i])/5)

for i in range(0, len(x)-1):
    ay.append((vy[i+1]-vy[i])/0.005/9.81)
    az.append((vz[i+1]-vz[i])/0.005/9.81)
    ax.append((vx[i+1]-vx[i])/0.005/9.81)
    a.append(math.sqrt(ay[i]**2 + ax[i]**2 + az[i]**2) + 1)
    #corr += a[i] * acc[i]
    #amoc += a[i] * a[i]
    #accmoc += acc[i] * acc[i]
#amoc /=  len(a)
#accmoc /=  len(a)
#corr /= len(a)
#corr /= math.sqrt(amoc * accmoc)
#print(corr)


for i in range (0, len(x) -1):
    if(acc[i] > 30):
        acc[i] = 30


#acc = butter_lowpass_filter(acc,cuttoff, fs, order=oreder)







#print(scipy.signal.find_peaks(y, height=300))



jerk = [0]
for i in range(1, len(acc)):
    jerk.append(abs((acc[i] - acc[i - 1]))/0.005)

"""
N = 10
avgAcc = []
for i in range(0, len(acc)):
    if i < N-1:
        avgAcc.append(0)
    else:
        avgAcc.append(1/(N) * sum(acc[i-N:i]))




#set time to run from 0
time[:] = time[:] - time[0]
#modify time to seconds
time = time / 1000





#plt.plot(time,force, label='y[t]')
plt.plot(time,acc, label='jerk')
plt.plot(time,avgAcc, label='acceleration')
#plt.legend
#plt.ylim(-3, 1000)


#ticks = [2,3,4,6,7,8,10,12]
#plt.yticks( ticks)

plt.xlabel("čas [s]",fontsize=15)
plt.ylabel("pospešek[g]",fontsize=15)


plt.show()



