PATHTOFILE = "PUT YOUR DIR OF CHOICE"
IMUSTAN = "Healthy"
MOTORSTATE = f"RawData\\{IMUSTAN}\\"
PATHTORESULTIMAGE = f"{PATHTOFILE}\\{MOTORSTATE}"
AxFile = open(f"{PATHTORESULTIMAGE}Ax.txt","r")
AyFile = open(f"{PATHTORESULTIMAGE}Ay.txt","r")
AzFile = open(f"{PATHTORESULTIMAGE}Az.txt","r")
AxFile = open(f"{PATHTORESULTIMAGE}Ax.txt","r")
AyFile = open(f"{PATHTORESULTIMAGE}Ay.txt","r")
AzFile = open(f"{PATHTORESULTIMAGE}Az.txt","r")
GxFile = open(f"{PATHTORESULTIMAGE}Gx.txt","r")
GyFile = open(f"{PATHTORESULTIMAGE}Gy.txt","r")
GzFile = open(f"{PATHTORESULTIMAGE}Gz.txt","r")
CSVFILE = f"FreqTime{IMUSTAN}.csv"

import csv
import numpy as np
from scipy.fft import rfft, rfftfreq
from scipy.signal import butter, filtfilt
import numpy as np
from Filters import ButterFilters

highPassFilter = ButterFilters('high',3,10,500,False)

iteration = 0
Ax = []
Ay = []
Az = []
Gx = []
Gy = []
Gz = []

def SplitDataIntoList(param):
    X = [];param1 = []
    for i in range(0,67200):
        param1.append(param.readline())
    for i in range(0,len(param1)):
        temp = []
        param1[i] = param1[i][1:-2]
        param1[i] = param1[i].split(', ')
        for y in param1[i]:
            
            temp.append(float(y))
        X.extend(temp)
    return X


Ax = SplitDataIntoList(AxFile)
Ay = SplitDataIntoList(AyFile)
Az = SplitDataIntoList(AzFile)

Gx = SplitDataIntoList(GxFile)
Gy = SplitDataIntoList(GyFile)
Gz = SplitDataIntoList(GzFile)
ax_avr = [];ay_avr = [];az_avr = []
gx_avr = [];gy_avr = [];gz_avr = []

Ax=highPassFilter.butter_highpass_filter(Ax);Ay=highPassFilter.butter_highpass_filter(Ay);Az=highPassFilter.butter_highpass_filter(Az)
Gx=highPassFilter.butter_highpass_filter(Gx);Gy=highPassFilter.butter_highpass_filter(Gy);Gz=highPassFilter.butter_highpass_filter(Gz)

ax_avr=(np.average(Ax));ay_avr=(np.average(Ay));az_avr=(np.average(Az))
gx_avr=(np.average(Ax));gy_avr=(np.average(Ay));gz_avr=(np.average(Az))

def WriteToCSV(file,a,b,c):


    
    ## Features
    a_Max=np.max(a)
    b_Max=np.max(b)
    c_Max=np.max(c)

    a_Med = np.median(a)
    b_Med = np.median(b)
    c_Med = np.median(c)

    a_Min=np.min(a)
    b_Min=np.min(b)
    c_Min=np.min(c)

    a_PTP = a_Max-a_Min
    b_PTP = b_Max-b_Min
    c_PTP = c_Max-c_Min

    a_var = np.var(a)
    b_var = np.var(b)
    c_var = np.var(c)

    a_stdev = np.sqrt(a_var)
    b_stdev = np.sqrt(b_var)
    c_stdev = np.sqrt(c_var) 

    ayfft = rfft(a)
    afft = rfftfreq(len(a), 1/500)
    afft  =afft[0:50]
    ayfft  =ayfft[0:50]

    byfft = rfft(b)
    bfft = rfftfreq(len(b), 1/500)
    bfft  =bfft[0:50]
    byfft  =byfft[0:50]

    cyfft = rfft(c)
    cfft = rfftfreq(len(c), 1/500)
    cfft  =cfft[0:50]
    cyfft  =cyfft[0:50]



    aMax = np.max(np.abs(ayfft))
    aMin = np.min(np.abs(ayfft))
    bMax= np.max(np.abs(byfft))
    bMin= np.min(np.abs(byfft))
    cMax= np.max(np.abs(cyfft))
    cMin= np.min(np.abs(cyfft))
    aPTP = aMax-aMin
    bPTP = bMax-bMin
    cPTP = cMax-cMin 

    with open(file, 'a+', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([a_stdev,a_var,a_Med,a_Min,a_Max,a_PTP,b_stdev,b_var,b_Med,b_Min,b_Max,b_PTP,c_stdev,c_var,c_Med,c_Min,c_Max,c_PTP,aMax,aMin,aPTP,bMax,bMin,bPTP,cMax,cMin,cPTP,1])
    file.close()



for i in range(0,len(Ax)):
        Ax[i] = Ax[i]-ax_avr
        Ay[i] = Ay[i]-ay_avr
        Az[i] = Az[i]-az_avr
        Gx[i] = Gx[i]-gx_avr
        Gy[i] = Gy[i]-gy_avr
        Gz[i] = Gz[i]-gz_avr


for i in range(1,len(Ax),255):
    Ax_temp = [];
    Gx_temp = [];
    Gy_temp = [];

    Ax_temp = Ax[i:i+255];

    Gy_temp = Gy[i:i+255];
    Gx_temp = Gx[i:i+255];

    WriteToCSV(CSVFILE,Ax_temp,Gx_temp,Gy_temp)


