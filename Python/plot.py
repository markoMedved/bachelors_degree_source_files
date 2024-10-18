import matplotlib.pyplot as plt
from nptdms import TdmsFile
from datetime import date

#path to tdms file, if the experiment wasn't today, set date manually, file always manual
#path = "TDMS/" + str(date.today()) + "/D-03-14-17-26-09.tdms"
path =""


#read tdms file
with TdmsFile.open(path) as file:
    #all data
    data = file["DATA"] 
    #absolute acceleration array
    accx = data["Ax1"][:]
    accy = data["Ay1"][:]
    accz = data["Az1"][:]
    gx = data["Gx1"][:]
    gy = data["Gy1"][:]
    gz = data["Gz1"][:]
    #time array
    time = data["LV Ts"][:]



#set time to run from 0
time[:] = time[:] - time[0]
#modify time to seconds
time = time / 1000


#plot acceleration in dependence of time
plt.figure(1)
plt.subplot(3,1,1)
plt.plot(time,accx)

plt.subplot(3,1,2)
plt.plot(time,accy)

plt.subplot(3,1,3)
plt.plot(time,accz)
plt.show()

plt.figure(2)
plt.subplot(3,1,1)
plt.plot(time,gx)

plt.subplot(3,1,2)
plt.plot(time,gy)

plt.subplot(3,1,3)
plt.plot(time,gz)
plt.show()

