import paho.mqtt.client as mqtt
import os
import json
import api_caller

class Messenger:
    def __init__(self):
        self.connected = False

        #TravelService-Object erstellen
        self.newsApiCaller = api_caller.WorldNewsApiCaller()
        
        self.location : dict = None

        #aufbau der MQTT-Verbindung
        self.mqttConnection = mqtt.Client()
        self.mqttConnection.on_connect = self.__onMQTTconnect
        self.mqttConnection.on_message = self.__onMQTTMessage

        #Definition einer Callback-Funktion für ein spezielles Topic
        self.mqttConnection.message_callback_add("req/news/<Anzahl der Artikel>", self.__newsServiceCallback)
        self.mqttConnection.message_callback_add("location/current", self.__locationUpdateCallback)

    def connect(self):
        if not self.connected:
            try:
                docker_container = os.environ.get('DOCKER_CONTAINER', False)
                if docker_container:
                    mqtt_address = "broker"
                else:
                    mqtt_address = "localhost"
                self.mqttConnection.connect(mqtt_address,1883,60)
            except:
                return False
        self.connected = True
        return True
    
    def disconnect(self):
        if self.connected:
            self.connected = False
            self.mqttConnection.disconnect()
        return True

    def __onMQTTconnect(self,client,userdata,flags, rc):
        client.subscribe([("req/news/<Anzahl der Artikel>",0), ("location/current", 0)])

    def __onMQTTMessage(self,client, userdata, msg):
        pass

    def __locationUpdateCallback(self,client, userdata, msg):
        try:
            locationData = json.loads(str(msg.payload.decode("utf-8")))
        except:
            print("Can't decode message")
            return
        
        reqKeys = ['latitude', 'longitude']

        if not all(key in locationData for key in reqKeys):
            print("not all keys available")
            return
        
        self.location = {
            'latitude': locationData['latitude'],
            'longitude': locationData['longitude']
        }

    def __newsServiceCallback(self,client, userdata, msg):
        try:
            newsApiArguments = json.loads(str(msg.payload.decode("utf-8")))
        except:
            print("Can't decode message")
            return
        
        reqKeys = ['numArticles']

        if not all(key in newsApiArguments for key in reqKeys):
            print("not all keys available")
            return

        newsData = self.newsApiCaller.newsRequest(newsApiArguments['numArticles'], self.location)

        if newsData != -1:
            for article in newsData:
                self.mqttConnection.publish("news/article",json.dumps(article))

    def foreverLoop(self):
        self.mqttConnection.loop_forever()