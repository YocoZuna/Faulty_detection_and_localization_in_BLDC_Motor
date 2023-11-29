import MQTT
from Filters import Moving_Avgr_Filter
import numpy as np
from PIL import Image
AvrFilter = Moving_Avgr_Filter(100)
iteration = 0 
current_iter = 0

class Current_Monitor(MQTT.Mqtt):
    BUFFOR_LEN = 19312
    def __init__(self, q, MQTT_server, MQTT_create, MQTT_subscribe):
        super().__init__(q, MQTT_server, MQTT_create, MQTT_subscribe)

    def on_message(self,client, userdata, message):
        CurrentList = []
        ResultArray = [[],[],[]]

        for i in range(0,self.BUFFOR_LEN,2):
            y  = i+2
            CurrentList.append((int.from_bytes(message.payload[i:y], "little")))


 
        ################################ Applying moving filter
        for i in CurrentList[0:3200]:
            a = i
            ResultArray[0].append(a)
            
        for i in CurrentList[3201:6401]:
            b= i
            ResultArray[1].append(b)
        for i in CurrentList[6402:9602]:
            c= i
            ResultArray[2].append(c)

        self.queue.put(ResultArray)

    def CreateImage(self,pa,pb,pc,PrevValue):
        pa_RGB = []
        pb_RGB = []
        pc_RGB = []

        if iteration ==0:
            pa_RGB = PrevValue[0]
            pb_RGB = PrevValue[1]
            pc_RGB = PrevValue[2]
        if iteration!= 0:
            pa_RGB = PrevValue[0][-32:]
            pb_RGB = PrevValues[1][-32:]
            pc_RGB = PrevValues[2][-32:]
        pa_RGB.extend(pa)
        pb_RGB.extend(pb)
        pc_RGB.extend(pc)

        global current_iter

        pa_RGB=AvrFilter.Filter_Fill2(pa_RGB)
        pb_RGB=AvrFilter.Filter_Fill2(pb_RGB)
        pc_RGB=AvrFilter.Filter_Fill2(pc_RGB)
        pa_avr = np.average(pa_RGB)
        pb_avr = np.average(pb_RGB)
        pc_avr = np.average(pc_RGB)

        for i in range(0,len(pa_RGB)):
            pa_RGB[i] = pa_RGB[i]-pa_avr
            pb_RGB[i] = pb_RGB[i]-pb_avr
            pc_RGB[i] = pc_RGB[i]-pc_avr




            
        minima = np.min(pa_RGB)
        pa_RGB = [x - minima for x in pa_RGB]
        maxima = np.max(pa_RGB)
        pa_RGB = [x * (255/maxima) for x in pa_RGB]

        minima = np.min(pb_RGB)
        pb_RGB = [x - minima for x in pb_RGB]
        maxima = np.max(pb_RGB)
        pb_RGB = [x * (255/maxima) for x in pb_RGB]

        minima = np.min(pc_RGB)
        pc_RGB = [x - minima for x in pc_RGB]
        maxima = np.max(pc_RGB)
        pc_RGB = [x * (255/maxima) for x in pc_RGB]
        for i in range(0,len(pa_RGB)):
            pa_RGB[i] = int(np.round(pa_RGB[i]))
            pb_RGB[i] = int(np.round(pb_RGB[i]))
            pc_RGB[i] = int(np.round(pc_RGB[i]))

        for i in range(0,2800,255):
            current_iter = current_iter+1
            pa_temp = pa_RGB[i:i+255]
            pb_temp = pb_RGB[i:i+255]
            pc_temp = pc_RGB[i:i+255]


            add_zeros_pa = 0
            add_zeros_pb = 1
            add_zeros_pc = 1
            for y in range(0, len(pa_temp)):
                pa_temp.insert(add_zeros_pa+1, 0)
                pa_temp.insert(add_zeros_pa+2, 0)
                add_zeros_pa = add_zeros_pa + 3

            for z in range(0, len(pa_temp)):
                pb_temp.insert(add_zeros_pb-1, 0)
                pb_temp.insert(add_zeros_pb+1, 0)
                add_zeros_pb = add_zeros_pb + 3

            for x in range(0, len(pa_temp)):
                pc_temp.insert(add_zeros_pc-1, 0)
                pc_temp.insert(add_zeros_pc-1, 0)
                add_zeros_pc = add_zeros_pc + 3

        
            pa_temp1 = np.asarray(pa_temp)
            pa_temp1 = pa_temp1.astype(np.uint8)
            pa_temp1 = np.resize(pa_temp1, (16,16,3))

            pb_temp1 = np.asarray(pb_temp)
            pb_temp1 = pb_temp1.astype(np.uint8)
            pb_temp1 = np.resize(pb_temp1, (16,16,3))

            pc_temp1 = np.asarray(pc_temp)
            pc_temp1 = pc_temp1.astype(np.uint8)
            pc_temp1 = np.resize(pc_temp1, (16,16,3))


            imr = Image.fromarray(pa_temp1)
            img = Image.fromarray(pb_temp1)
            imb = Image.fromarray(pc_temp1)
            finalimg = pa_temp1+pb_temp1+pc_temp1

            final = Image.fromarray(finalimg)
            final.save(f"{PATHTORESULTIMAGE}{current_iter}.png")




            pa_temp.clear()
            pb_temp.clear()
            pc_temp.clear()
            
queue = MQTT.mp.Queue()
Callback = Current_Monitor(queue,"localhost","Current_monitor","Motor")

PATHTOFILE = 'PUT HERE YOUR DIR OF CHOICE'
MOTORSTATE = "Current\\Broken_Bearing"

PATHTORESULTIMAGE = f"{PATHTOFILE}\\{MOTORSTATE}\\"  

if __name__ == "__main__":
    # Gx Gy Gz Ax Ay Az

    PrevValues = [[],[],[]]
    ## Adding zero at the begginig intital value 
    for i in range (0,len(PrevValues)):
        for z in range(0,32):
            PrevValues[i].append(0)
    StartMqttInOtherProces = MQTT.mp.Process(target=Callback.CreateProcesWithMqtt)
    StartMqttInOtherProces.start()
    

    while 1:
        ia=0;ib=0;ic = 0
        QueadResultArray = [ia,ib,ic]
        if (queue.empty()):
            continue
        else:
            for i in range(0,1):
                temp = queue.get()
                ia = temp[0]
                ib = temp[1]
                ic = temp[2]

            Callback.CreateImage(ia,ib,ic,PrevValues)
            PrevValues  =[ia,ib,ic]
            iteration +=1
        if current_iter >2100:
            print("Done")
            exit()