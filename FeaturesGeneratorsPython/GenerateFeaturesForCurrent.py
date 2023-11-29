PATHTOFILE = 'PUT YOUR DIR OF CHOICE'
CurrentStan = "Healthy"
MOTORSTATE = f"RawData\\{CurrentStan}\\"
PATHTORESULTIMAGE = f"{PATHTOFILE}\\{MOTORSTATE}"
IaFile = open(f"{PATHTORESULTIMAGE}Ia.txt","r")
IbFile = open(f"{PATHTORESULTIMAGE}Ib.txt","r")
IcFile = open(f"{PATHTORESULTIMAGE}Ic.txt","r")

CSVFILE = f"TimeCurrent{CurrentStan}.csv"

import csv
import numpy as np
from scipy.fft import rfft, rfftfreq
import numpy as np
from Filters import Moving_Avgr_Filter
Mv = Moving_Avgr_Filter(100)


Ia = []
Ic = []
Ib = []
IaResult = []
IbResult = []
IcResult = []
iteration = 0

def SplitDataIntoList(param):
    X = [];param1 = []
    for i in range(0,210):
        param1.append(param.readline())
    for i in range(0,len(param1)):
        temp = []
        param1[i] = param1[i][1:-2]
        param1[i] = param1[i].split(', ')
        for y in param1[i]:
            
            temp.append(int(y))
        X.extend(temp)
    return X

 
Ia = SplitDataIntoList(IaFile)
Ib = SplitDataIntoList(IbFile)
Ic = SplitDataIntoList(IcFile)

Ia_avr = [];Ib_avr = [];Ic_avr = []
Iaf = []
Ibf = []
Icf = []

for i in range(0,len(Ia),3200):
    Iaf.append(Mv.Filter_Fill2(Ia[i:i+3200]));
    Ibf.append(Mv.Filter_Fill2(Ib[i:i+3200]));
    Icf.append(Mv.Filter_Fill2(Ic[i:i+3200]))


for i in range(0,len(Iaf)):
    Ia_avr.append((np.average(Iaf[i])));
    Ib_avr.append((np.average(Ibf[i])));
    Ic_avr.append((np.average(Icf[i])))


def WriteToCSV(file,a,b,c):

    ## Features
    a_MIa=np.max(a)
    b_MIa=np.max(b)
    c_MIa=np.max(c)

    a_Med = np.median(a)
    b_Med = np.median(b)
    c_Med = np.median(c)

    a_Min=np.min(a)
    b_Min=np.min(b)
    c_Min=np.min(c)

    a_PTP = a_MIa-a_Min
    b_PTP = b_MIa-b_Min
    c_PTP = c_MIa-c_Min

    a_var = np.var(a)
    b_var = np.var(b)
    c_var = np.var(c)

    a_stdev = np.sqrt(a_var)
    b_stdev = np.sqrt(b_var)
    c_stdev = np.sqrt(c_var) 

    Ibfft = rfft(a)
    afft = rfftfreq(len(a), 1/500)
    afft  =afft[0:50]
    Ibfft  =Ibfft[0:50]

    byfft = rfft(b)
    bfft = rfftfreq(len(b), 1/500)
    bfft  =bfft[0:50]
    byfft  =byfft[0:50]

    cyfft = rfft(c)
    cfft = rfftfreq(len(c), 1/500)
    cfft  =cfft[0:50]
    cyfft  =cyfft[0:50]



    aMIa = np.max(np.abs(Ibfft))
    aMin = np.min(np.abs(Ibfft))
    bMIa= np.max(np.abs(byfft))
    bMin= np.min(np.abs(byfft))
    cMIa= np.max(np.abs(cyfft))
    cMin= np.min(np.abs(cyfft))
    aPTP = aMIa-aMin
    bPTP = bMIa-bMin
    cPTP = cMIa-cMin 

    with open(file, 'a+', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([a_stdev,a_var,a_Med,a_Min,a_MIa,a_PTP,b_stdev,b_var,b_Med,b_Min,b_MIa,b_PTP,c_stdev,c_var,c_Med,c_Min,c_MIa,c_PTP,aMIa,aMin,aPTP,bMIa,bMin,bPTP,cMIa,cMin,cPTP,1])
    file.close()

IaNew = []
IbNew = []
IcNew = []

for i in range(0,len(Iaf)):
        
        for y in range (0,3100):
            temp= Iaf[i][y]
            temp2 = Ia_avr[i]
            IaNew.append((temp-temp2))
for i in range(0,len(Ibf)):

        for y in range (0,3100):
            temp= Ibf[i][y]
            temp2 = Ib_avr[i]
            IbNew.append((temp-temp2))
for i in range(0,len(Icf)):

        for y in range (0,3100):
            temp= Icf[i][y]
            temp2 = Ic_avr[i]
            IcNew.append((temp-temp2))

# 255 probek 

for i in range(1,len(IaNew),255):
    Ia_temp = [];
    Ib_temp = [];
    Ic_temp = [];

    Ia_temp = IaNew[i:i+255];

    Ib_temp = IbNew[i:i+255];
    Ic_temp = IcNew[i:i+255];

    WriteToCSV(CSVFILE,Ia_temp,Ib_temp,Ic_temp)


