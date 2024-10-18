import matplotlib.pyplot as plt
from nptdms import TdmsFile
from datetime import date
import math
from scipy.signal import butter, lfilter, freqz

#skupaj poglej skoke in tek krivuljo
#višine pristanke more bit višja
#mogoče da se pred vsakim skokom more pomirit preden prideš v before state, z povprečjem
#če prebere skok prej in nato prehitro še enega(preveri čas konca skoksa - čas konca prejšni - čas skoka)
#če je biv vmes acc v določenih mejah potem gre prejšnji skok ven
#dodajanje pogojev za peake


#x je levo desno, y je gordol, z je naprej nazaj

#pravilno prebere samo skoke katerekoli
#zmoti se pri: gibanjih ki dajo zelo podobno ven


#path to tdms file, if the experiment wasn't today, set date manually, file always manual
#path = "TDMS/" + str(date.today()) + "/D-03-14-17-26-09.tdms"
path =""

#read tdms file
with TdmsFile.open(path) as file:
    #all data
    data = file["DATA"] 
    #absolute acceleration array, odvisno kere poskuse gledaš
    acc = data["empty1"][:]
    #accx = data["Ax1"][:]
    #accy = data["Ay1"][:]
    #accz = data["Az1"][:]
    #time array
    time = data["LV Ts"][:]


#prvi dan snemanja je bil v napačno smer obrnjen zato je -1ka zraven
#acc = []
#for i in range(0, len(accx)):
 #   acc.append(math.sqrt(accx[i] * accx[i] + accy[i] * accy[i] + accz[i] * accz[i]))
    
    

#set time to run from 0
time[:] = time[:] - time[0]
#modify time to seconds
time = time/1000

#sample time in milis
sampleTime = 5

#get flight time and counter
#initializing array for jump times
jumpTimes = []
#time of jump
flightTime= 0
indexStart = 0
indexEnd = 0
#jump counter
counter = 0

#decision boundaries
#when the jump action starts
takeoffStartAcc = 6
#acc when fly state is triggered
flyStartAcc =3
#trigger for landing 
landingMinAcc = 5
endLanding = 2
#timer for eliminating errors beacuse of fluctuations
timer = 0

#state before the jumping event 
jump = "before"

#if timeOut
timeOut = False

#how much time to go back when going into takeoff state to calculate mean before takeoff
timeLapse = 15
timeLapseIndex = int(timeLapse/sampleTime)

#at the last part of flight mean is low
timeLapseLand = 15
timeLapseIndexLand = int(timeLapseLand/sampleTime)

#jerk boundaries
takeoffJerk =  1 #prej na 3
landJerk = 1 #prej na 10
firstTime = True

#moving average
N = 10
avgAcc =[]



for i in range(0, len(acc)):
    if i < N-1:
        avgAcc.append(0)
    else:
        avgAcc.append(1/(N) * sum(acc[i-N:i]))

    #jerk, ena možnost je tut tabelo nrdit pa gledat potek
    if i > 1:
        jerk = (acc[i] - acc[i - 1])/(sampleTime/10)
            
    #remember the first time when the acc > 5 - for more correct height
    if acc[i] >= takeoffStartAcc and jump == "before" and (timer > 100 or timeOut == True) and validBeforeState == True and firstTime == True:
        start = i
        firstTime = False
        print("first time", time[i])
    
    if firstTime == False and time[i] - time[start] > 0.02:
        firstTime = True
        
    
    if acc[i] >= takeoffStartAcc and jump == "before" and (timer > 100 or timeOut == True) and validBeforeState == True and jerk >= takeoffJerk:
        #print("time and mean: ",time[i], meanBefore)
        #state-takeoff,after the acceleration has exceeded the boundary, before takeoff
        print("takeoff",time[i])
        jump = "takeoff"        
        indexStart = start
        #reseting timer, and values for evaluating jump
        timer = 0     
        timeOut = False
        firstTime = True
        decisionMade = False
      
        
        
    elif acc[i] <= flyStartAcc and jump == "takeoff" and timer > 30:
        #state-fly, during flying in the air
        jump = "fly"
        timer = 0
    
        
    elif acc[i] > landingMinAcc and jump == "fly" and timer > 200 and jerk >= landJerk:
        #state-land, when landing landing
        jump = "land"
        indexEndOld = indexEnd
        indexEnd = i
        #calculating flight  time from start and end indices
        flightTime = time[indexEnd] - time[indexStart]
        timer = 0
            
        #mean before landing has to be quite low
        validLand = True
        back = int(200/sampleTime)
        if i > back + timeLapseIndexLand:
            for j in range(i - back - timeLapseIndexLand, i - timeLapseIndexLand):        
                if avgAcc[j] > meja:
                    validLand = False
                    
      
       
        
    elif acc[i] <= endLanding and jump == "land" and timer > 30:
          
        #do not count low jumps, they are probably steps
        if timer < 150 and validLand == True and flightTime > 0.35:
            #writing flight times into array
            jumpTimes.append(flightTime)
            #jump recordings
            print("jump: " + str(time[indexStart]), time[indexEnd])

            #documenting the jump
            counter = counter +1
        #resetting flight time
        flightTime = 0
        #reseting the state
        jump = "before"
        timer = 0
       

    #if takeoff takes too long, it is not a jump - poglej če kaj dela sploh
    if jump == "takeoff" and timer > 200:
        jump = "before"
        timer = 0
        print("takeoff cant be that long")

    if jump == "land" and timer > 100:
        jump = "before"
        timer = 0
        print("landing cant be that long")
      
    #if jump is more than 1.1s -> 1.5 m -> no one can jump that high
    if time[i]- time[indexStart] > 1 and jump == "fly":    
        jump = "before"
        timer = 0
        timeOut = True
        print("too long: " + str(time[indexStart]), time[i])

   #checking if the filtered signal is within boundaries
    if  jump == "before" and firstTime == True:
        validBeforeState = True
        timeBack = 80
        back = int(timeBack/sampleTime)       
        if i > back + timeLapseIndex:
            for j in range(i - back - timeLapseIndex, i - timeLapseIndex):
                if avgAcc[j] > 2 or avgAcc[j] < 0.6:
                   validBeforeState = False
    

    #if during first part of fly a avgacc is high set the limit for second part of fly higher 
    if jump ==  "fly" and timer < 150 and timer > 50 and avgAcc[i] > 7 and decisionMade == False:
        meja = 10
        decisionMade = True
        print("time", time[i])

    elif jump == "fly" and decisionMade == False:
        meja = 10

        
    #increasing timer by sampletime every iteration
    timer  = timer + sampleTime


print(counter)
print(jumpTimes) 

#get height from time
g = 9.81
height = []
for j in range(0, len(jumpTimes)):
    height.append(g * jumpTimes[j] * jumpTimes[j]/8)
print(height)

