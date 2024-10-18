import matplotlib.pyplot as plt
from nptdms import TdmsFile
from datetime import date
import math
import numpy as np
import scipy
import scipy.integrate

path =""


#read tdms file
with TdmsFile.open(path) as file:
    #all data
    data = file["DATA"] 
    #absolute acceleration array, odvisno kere poskuse gledaš
    F1 =   data["Force z1"][:] +  data["Force z2"][:]
    #F2 = data["Force z2"][:]
    time = data["LV Ts"][:]


avg = np.average(F1[0:300])

F1 -= avg
F1 /= (avg/9.81) #deljenje z maso

v = 0
for i in range(5554, 5646):
    v+= F1[i] * 0.005

h = v**2/(2*9.81)
print(v)
