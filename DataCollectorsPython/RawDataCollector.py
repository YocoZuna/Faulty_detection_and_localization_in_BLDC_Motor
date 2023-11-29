import MQTT

PATHTOFILE = 'PUT HERE YOUR DIR OF CHOICE'
MOTORSTATE = "Rawdata\\Faulty_WH"
PATHTORESULTIMAGE = f"{PATHTOFILE}\\{MOTORSTATE}\\"
IaFile = open(f"{PATHTORESULTIMAGE}Ia.txt","a+")
IbFile = open(f"{PATHTORESULTIMAGE}Ib.txt","a+")
IcFile = open(f"{PATHTORESULTIMAGE}Ictxt","a+")
AxFile = open(f"{PATHTORESULTIMAGE}Ax.txt","a+")
AyFile = open(f"{PATHTORESULTIMAGE}Ay.txt","a+")
AzFile = open(f"{PATHTORESULTIMAGE}Az.txt","a+")
GxFile = open(f"{PATHTORESULTIMAGE}Gx.txt","a+")
GyFile = open(f"{PATHTORESULTIMAGE}Gy.txt","a+")
GzFile = open(f"{PATHTORESULTIMAGE}Gz.txt","a+")
iteration = 0
class  Raw_Data_Collector(MQTT.Mqtt):
    
    iteration = 0
    GYRO_RESOLUTION = 131.00
    ACC_RESOLUTION =  16384.00
    BUFFOR_LEN = 19312
    def __init__(self, q, MQTT_server, MQTT_create, MQTT_subscribe):
        super().__init__(q, MQTT_server, MQTT_create, MQTT_subscribe)


    def on_message(self,client, userdata, message):
        CurrentList = []
        ia = []
        ib = []
        ic = []
        Ax = []
        Ay = []
        Az = []
        Gx = []
        Gy = []
        Gz = []

        
        self.iteration = self.iteration+1
        # Decoding data
        for i in range(0,self.BUFFOR_LEN,2):
            y  = i+2
            CurrentList.append((int.from_bytes(message.payload[i:y], "little")))


        #Currents
        for i in CurrentList[0:3200]:
            a = i
            ia.append(a)
            
        for i in CurrentList[3201:6401]:
            b= i
            ib.append(b)
        for i in CurrentList[6402:9602]:
            c= i
            ic.append(c)
        #Gyro
        for i in CurrentList[9603:9611]:
            Gx.append(float(i)/self.GYRO_RESOLUTION)
        for i in CurrentList[9612:9620]:
            Gy.append(float(i)/self.GYRO_RESOLUTION)
        for i in CurrentList[9621:9629]:
            Gz.append(float(i)/self.GYRO_RESOLUTION)
        for i in CurrentList[9630:9638]:
            Ax.append(float(i)/self.ACC_RESOLUTION)
        for i in CurrentList[9639:9647]:
            Ay.append(float(i)/self.ACC_RESOLUTION)
        for i in CurrentList[9648:]:
            Az.append(float(i)/self.ACC_RESOLUTION)

    
        self.queue.put([ia,ib,ic,Ax,Ay,Az,Gx,Gy,Gz])
    
    def WriteToFile(self,QueadResult):
        """Writing data to .txt files """
        IaFile.write(str(QueadResult[0])+"\n")
        IbFile.write(str(QueadResult[1])+"\n")
        IcFile.write(str(QueadResult[2])+"\n")
        AxFile.write(str(QueadResult[3])+"\n")
        AyFile.write(str(QueadResult[4])+"\n")
        AzFile.write(str(QueadResult[5])+"\n")
        GxFile.write(str(QueadResult[6])+"\n")
        GyFile.write(str(QueadResult[7])+"\n")
        GzFile.write(str(QueadResult[8])+"\n")
queue = MQTT.mp.Queue()
Callback = Raw_Data_Collector(queue,"localhost","Raw_Data_Collector","Motor")

if __name__ == "__main__":
    StartMqttInOtherProces = MQTT.mp.Process(target=Callback.CreateProcesWithMqtt)
    StartMqttInOtherProces.start()
    while 1:
        QueadResultArray = [[],[],[],[],[],[],[],[],[]]
        if (queue.empty()):
            continue
        else:
            QueadResultArray = queue.get()
            Callback.WriteToFile(QueadResultArray)
            iteration += 1
