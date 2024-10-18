import matplotlib.pyplot as plt
from nptdms import TdmsFile
from datetime import date
import math

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
    acc = data["Ax1"][:]
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
time = time /1000


#sample time in milis
sampleTime = 5

#get flight time and counter

#initializing array for jump times, 5 slots
jumpTimes = [0 for i in range(0,7)]
#time of jump
flightTime= 0
indexStart = 0
indexEnd = 0
#jump counter
counter = 0
#decision boundaries
#when the jump action starts
decision = 5
#acc when fly state is triggered
flyStartAcc =6
#trigger for landing 
landingMinAcc = 10
endLanding = 2
#timer for eliminating errors beacuse of fluctuations
timer = 0
#state before the jumping event 
jump = "before"

#acceleration mean during fly
accMean = 0
startFly= 0
accMeanTresh = 6

#if timeOut
timeOut = False

#prevention
accTreshDuringFly = 5

previousWasJump = True

#mean during before state 
meanBefore = 0
meanBeforeTresh = 1.5
#how much time to go back when going into takeoff state to calculate mean before takeoff
timeLapse = 30
timeLapseIndex = int(timeLapse/sampleTime)

#at the last part of flight mean is low
meanflyTresh =3
timeLapseLand = 50
timeLapseIndexLand = int(timeLapseLand/sampleTime)

#jerk boundaries
#tole bo treba še pogruntat kako uno z first time nardit
takeoffJerk =  3 #prej na 3
landJerk = 7 #prej na 10
firstTime = True


for i in range(0, len(acc)):

    #jerk
    if i > 1:
        jerk = (acc[i] - acc[i - 1])/(sampleTime/10)
            
    #remember the first time when the acc > 5 - for more correct height
    if acc[i] >= decision and jump == "before" and (timer > 100 or timeOut == True) and meanBefore < meanBeforeTresh:
        start = i
        firstTime = False
        
    
    if acc[i] >= decision and jump == "before" and (timer > 100 or timeOut == True) and meanBefore < meanBeforeTresh  and jerk >= takeoffJerk:
        #print("time and mean: ",time[i], meanBefore)
        #state-takeoff,after the acceleration has exceeded the boundary, before takeoff
        jump = "takeoff"
        indexStartOld = indexStart
        indexStart = start
        #reseting timer, and values for evaluating jump
        timer = 0
        accMean = 0
        print(time[i])
        timeOut = False
        firstTime = True
      
        
      
        
    elif acc[i] <= flyStartAcc and jump == "takeoff" and timer > 30:
        #state-fly, during flying in the air
        jump = "fly"
        timer = 0
        #for calculating the average acc in fly state
        startFly = i
        #print("fly: ",time[i]
        
    elif acc[i] > landingMinAcc and jump == "fly" and timer > 300 and jerk >= landJerk:
        #state-land, when landing landing
        jump = "land"
        indexEndOld = indexEnd
        indexEnd = i
        #calculating flight  time from start and end indices
        flightTime = time[indexEnd] - time[indexStart]
        timer = 0
        #acc mean
        accMean = accMean - acc[i-1] - acc[i-2] #last few out
        accMean =  accMean/(i  - startFly-2)
        #print("mean: " + str(time[startFly]), time[i], accMean)
        
    elif acc[i] <= endLanding and jump == "land" and timer > 30:
          
        if accMean < accMeanTresh and timer < 150 and meanfly < meanflyTresh:
          
            #print(time[indexStart] - time[indexEndOld], time[indexStart],time[indexEndOld])
            #if another jump is shown to fast it means the previous jump wasn't the jump - it was the gather step
            if jumpTimes[0] > 0.1 and time[indexStart] - time[indexEndOld] < 0.5 and previousWasJump == True:
                counter = counter -1
                jumpTimes[counter] = 0
                print("penultimate: " + str(time[i]))

            #writing flight times into array
            jumpTimes[counter] = flightTime
            #jump recordings
            print("jump: " + str(time[indexStart]), time[indexEnd])

            #documenting the jump
            counter = counter +1

            previousWasJump = True
          
        else:
            previousWasJump = False
            #print("mean too high")
        
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
        previousWasJump = False
        
        
    #calculating average acc during fly
    if jump == "fly" and timer > 10:
        accMean = accMean + acc[i]
    

    #increasing timer by sampletime every iteration
    timer  = timer + sampleTime

    #if jump is more than 1.1s -> 1.5 m -> no one can jump that high
    if time[i]- time[indexStart] > 1 and jump == "fly":    
        jump = "before"
        timer = 0
        timeOut = True
        previousWasJump = False
        print("too long: " + str(time[indexStart]), time[i])

    #calculating mean in the state before
    #before jump the acceleration is really constant
    #tukaj če še ne bo delal lahko še zelo zaostriš samo pazt je treba da greš dovolj nazaj od začetka takeoffa
    if  jump == "before":
        meanBefore = 0
        back = int(100/sampleTime)
        
        if i > back + timeLapseIndex:
            for j in range(i - back - timeLapseIndex, i - timeLapseIndex):
                meanBefore = meanBefore + acc[j]
                
                if acc[j] > 2 or acc[j] < 0.8:
                   meanBefore = 100
                   
                
            meanBefore = meanBefore/(back)


    #mean before landing has to be quite low
    if  jump == "land":
        meanfly = 0
        back = int(200/sampleTime)
        
        if i > back + timeLapseIndexLand:
            for j in range(i - back - timeLapseIndexLand, i - timeLapseIndexLand):
                meanfly = meanfly + acc[j] 
            meanfly = meanfly/(back)
    
  
        

print(counter)
print(jumpTimes) 

#get height from time
g = 9.81
height = [0 for i in range (0,7)]
for j in range(0, len(jumpTimes)):
    height[j] = g * jumpTimes[j] * jumpTimes[j]/8
print(height)



