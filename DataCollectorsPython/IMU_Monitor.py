
import matplotlib.pyplot as plt
import numpy as np
import math
from scipy import signal as sp 
from colormap import Colormap
from PIL import Image
import MQTT
from Filters import ButterFilters
currentiter = 0
iteration = 0
highPassFilter = ButterFilters('high',3,10,500,False)
accimg = 0
gyroimg = 0
cm = Colormap()
my_cmap_red = cm.cmap_bicolor('black', 'red')
my_cmap_green = cm.cmap_bicolor('black', 'green')
my_cmap_blue = cm.cmap_bicolor('black', 'blue')


class IMU_Monitor(MQTT.Mqtt):
    def __init__(self, q, MQTT_server, MQTT_create, MQTT_subscribe):
        super().__init__(q, MQTT_server, MQTT_create, MQTT_subscribe)
   
    def on_message(self,client, userdata, message):


        GYRO_RESOLUTION = 131.00
        ACC_RESOLUTION =  16384.00
        BUFFOR_LEN = 19312
        CurrentList = []
        ia = []
        ib = []
        ic = []
      
        for i in range(0,BUFFOR_LEN,2):
            
            y  = i+2
            CurrentList.append((int.from_bytes(message.payload[i:y], "little")))

        ResultArray = [[],[],[],[],[],[]]

        for i in CurrentList[9603:9611]:
            ResultArray[0].append(float(i)/GYRO_RESOLUTION) #Gx
        for i in CurrentList[9612:9620]:
            ResultArray[1].append(float(i)/GYRO_RESOLUTION)
        for i in CurrentList[9621:9629]:
           ResultArray[2].append(float(i)/GYRO_RESOLUTION)#Gz
        for i in CurrentList[9630:9638]:
           ResultArray[3].append(float(i)/ACC_RESOLUTION)#Ax
        for i in CurrentList[9639:9647]:
            ResultArray[4].append(float(i)/ACC_RESOLUTION)
        for i in CurrentList[9648:]:
           ResultArray[5].append(float(i)/ACC_RESOLUTION)#Az

        
        self.queue.put(ResultArray)
    def STFT(self,paramX,paramY,paramZ,prev,name):
        
        param1 = []
        param2 = []
        param3 = []
        tempparam1 = []
        tempparam2 = []
        tempparam3 = []
        
            
        if name == "Acc" and iteration ==0:
                param1 = prev[3]
                param2 = prev[4]
                param3 = prev[5]
        elif name == "Gyro" and iteration ==0:
                param1 = prev[0]
                param2 = prev[1]
                param3 = prev[2]

        if iteration ==0:

            for i in paramX:
                for y in i:
                    param1.append(y)
            for i in paramY:
                for y in i:
                    param2.append(y)
            for i in paramZ:
                for y in i:
                    param3.append(y)

        if name == "Acc" and iteration >0:
            tempparam1 = prev[3][10:14]
            tempparam2 = prev[4][10:14]
            tempparam3 = prev[5][10:14]
        elif name == "Gyro" and iteration >0:
            tempparam1 = prev[0][10:14]
            tempparam2 = prev[1][10:14]
            tempparam3 = prev[2][10:14]

        if iteration >0:
            tempparam1 = tempparam1+paramX
            tempparam2 = tempparam2+paramY
            tempparam3 = tempparam3+paramZ
                                            
        
            for i in paramX: 
                for y in i:
                    param1.append(y)
            for i in paramY:
                for y in i:
                    param2.append(y)
            for i in paramZ:
                for y in i:
                    param3.append(y)
        
        param1 = highPassFilter.butter_highpass_filter(param1)
        param2 = highPassFilter.butter_highpass_filter(param2)
        param3 = highPassFilter.butter_highpass_filter(param3)


        window_length = 32;
        window = np.hamming(window_length);

        fs = 500

        
        signal = param1
        overlap = math.floor(window_length-1);
        fft_length = window_length*2;
        stft_frequency, stft_time, signal_stft = sp.stft(signal,fs=fs,window=window,nperseg=window_length,noverlap=overlap,nfft=fft_length,return_onesided=False);
        signal_stft = signal_stft[0:window_length-1,:];
        stft_frequency = stft_frequency[0:window_length-1];
        signal_stft_abs = abs(signal_stft);
        
        fig2 = plt.figure(2)

        plt.pcolormesh(stft_time, stft_frequency, signal_stft_abs, shading='nearest', cmap = my_cmap_green);
        fig2.canvas.draw()
        data2 = np.frombuffer(fig2.canvas.tostring_rgb(), dtype=np.uint8)
        data2 = data2.reshape(fig2.canvas.get_width_height()[::-1] + (3,))
        data2 = data2[58:428,80:577,:]

        signal = param2
        stft_frequency, stft_time, signal_stft = sp.stft(signal,fs=fs,window=window,nperseg=window_length,noverlap=overlap,nfft=fft_length,return_onesided=False);
        signal_stft = signal_stft[0:window_length-1,:];
        stft_frequency = stft_frequency[0:window_length-1];
        signal_stft_abs = abs(signal_stft);
        fig3 = plt.figure(3)

        plt.pcolormesh(stft_time, stft_frequency, signal_stft_abs, shading='nearest', cmap = my_cmap_blue);
        fig3.canvas.draw()
        data3 = np.frombuffer(fig3.canvas.tostring_rgb(), dtype=np.uint8)
        data3 = data3.reshape(fig3.canvas.get_width_height()[::-1] + (3,))
        data3 = data3[58:428,80:577,:]


            
        signal = param3
        stft_frequency, stft_time, signal_stft = sp.stft(signal,fs=fs,window=window,nperseg=window_length,noverlap=overlap,nfft=fft_length,return_onesided=False);
        signal_stft = signal_stft[0:window_length-1,:];
        stft_frequency = stft_frequency[0:window_length-1];
        signal_stft_abs = abs(signal_stft);
        fig4 = plt.figure(4)

        plt.pcolormesh(stft_time, stft_frequency, signal_stft_abs, shading='nearest', cmap = my_cmap_red);
        fig4.canvas.draw()
        data4 = np.frombuffer(fig4.canvas.tostring_rgb(), dtype=np.uint8)
        data4 = data4.reshape(fig4.canvas.get_width_height()[::-1] + (3,))
        data4 = data4[58:428,80:577,:]
        
        datargb = data2 + data3 + data4
        im = Image.fromarray(datargb)

        global accimg
        global gyroimg

        im.thumbnail((128,64))
        if name == "Acc":
            accimg = im
        elif name == "Gyro":
            gyroimg = im
        fig2.clear()
        fig3.clear()
        fig4.clear()

queue = MQTT.mp.Queue()
Callback = IMU_Monitor(queue,"localhost","IMU_monitor","Motor")

PATHTOFILE = 'PUT HERE YOUR DIR OF CHOICE'
MOTORSTATE = "IMU\\IDLE"

PATHTORESULTIMAGE = f"{PATHTOFILE}\\{MOTORSTATE}\\"  

if __name__ == "__main__":
    # Gx Gy Gz Ax Ay Az

    PrevValues = [[],[],[],[],[],[]]
    ## Adding zero at the begginig intital value 
    for i in range (0,len(PrevValues)):
        for z in range(0,32):
            PrevValues[i].append(0)
    StartMqttInOtherProces = MQTT.mp.Process(target=Callback.CreateProcesWithMqtt)
    StartMqttInOtherProces.start()
    

    while 1:
        
        QueadResultArray = [[],[],[],[],[],[]] 
        if (queue.empty()):
            continue
        else:
            for i in range(0,28):
                temp = queue.get()
                for i in range(0,6):
                    QueadResultArray[i].append(temp[i])

            Callback.STFT(QueadResultArray[3],QueadResultArray[4],QueadResultArray[5],PrevValues,"Acc")
            Callback.STFT(QueadResultArray[0],QueadResultArray[1],QueadResultArray[2],PrevValues,"Gyro")
            
            PrevValues = QueadResultArray


            ImageFinal = Image.new("RGB",(64,128),"white")
            ImageFinal.paste(accimg,(0,0))
            ImageFinal.paste(gyroimg,(0,64))
            
            ImageFinal.save(f"{PATHTORESULTIMAGE}{iteration}.png")
            iteration +=1
            accimg = 0
            gyroimg = 0


        