from scipy.signal import butter, filtfilt
import numpy as np

class ButterFilters:
    def __init__(self,type,order,cutoff,fs,analog):
        self.cutoff = cutoff
        self.type = type
        self.order = order
        self.analog = analog
        self.fs = fs
    def butter_highpass(self,cutoff,fs,order=5):
        nyq = 0.5 * fs
        self.normal_cutoff = cutoff / nyq
        b, a = butter(self.order, self.normal_cutoff, self.type, analog=self.analog)
        return b, a

    def butter_highpass_filter(self,data):
        b, a = self.butter_highpass(self.cutoff, self.fs, order=self.order)
        y = filtfilt(b, a,data)
        return y

class Moving_Avgr_Filter:


    def __init__(self,number_of_points):
   
        
        self.moving_coeff = []
        self.points = number_of_points
        
        for i in range(0,self.points):
            self.moving_coeff.append(0.1)
    
        self.buff = []
        for y in range(0,len(self.moving_coeff)):
            self.buff.append(0.0) 
        self.buffIndex = 0
        self.out = 0

    def Filter_Fill(self,input):
        


        self.buff[self.buffIndex] = input


        self.buffIndex = self.buffIndex+1

        if self.buffIndex == len(self.moving_coeff):
            self.buffIndex = 0 
       
        self.out = 0

        self.sumIndex = self.buffIndex

        for n in range(0,len(self.moving_coeff)):

            if self.sumIndex > 0:
                self.sumIndex = self.sumIndex-1
            else:
                self.sumIndex = len(self.moving_coeff)-1

            self.temp1 = float(self.moving_coeff[n])
            self.temp2 = float(self.buff[self.sumIndex])

            self.out = self.out + self.temp1 * self.temp2
        return float(self.out)

    def Filter_Fill2(self,input):
        
        import numpy as np 
        
        window_size  = 100
        
        i = 0
        self.moving_averages = [] 
        while i < len(input) - window_size + 1: 
            window_average = round(np.sum(input[ 

            i:i+window_size]) / window_size, 2) 

            self.moving_averages.append(window_average) 

            i += 1
        return self.moving_averages