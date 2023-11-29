import multiprocessing as mp 
import paho.mqtt.client as mqtt
class  Mqtt(mp.Process):

    def __init__(self,q,MQTT_server,MQTT_create,MQTT_subscribe):
        self.queue = q
        self.topic = MQTT_create
        self.subscribe = MQTT_subscribe
        self.server = MQTT_server
        mp.Process.__init__(self)


    def on_message(self,client, userdata, message):

    ## This is interface
        pass
            
         

    def CreateProcesWithMqtt(self):
        mqttBroker  = self.server

        client = mqtt.Client(self.topic)
        client.connect(mqttBroker) 
        ## Open files 

        client.subscribe(self.subscribe)
        client.loop_start()
        while 1:
            
            client.on_message=self.on_message


        client.loop_stop()
