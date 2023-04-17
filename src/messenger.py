import paho.mqtt.client as mqtt
import os
import json
import api_caller

class Messenger:
    def __init__(self):
        self.connected = False

        #TravelService-Object erstellen
        self.newsApiCaller = api_caller.WorldNewsApiCaller()

        #aufbau der MQTT-Verbindung
        self.mqttConnection = mqtt.Client()
        self.mqttConnection.on_connect = self.__onMQTTconnect
        self.mqttConnection.on_message = self.__onMQTTMessage

        #Definition einer Callback-Funktion für ein spezielles Topic
        self.mqttConnection.message_callback_add("req/news", self.__newsServiceCallback)

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
        client.subscribe([("req/news",0)])

    def __onMQTTMessage(self,client, userdata, msg):
        pass

    def __newsServiceCallback(self,client, userdata, msg):
        try:
            newsApiArguments = json.loads(str(msg.payload.decode("utf-8")))
        except:
            print("Can't decode message")
            return

        if not 'numArticles' in newsApiArguments:
            print("numArticles not specified")
            return

        location = None
        if 'location' in newsApiArguments:
            if 'latitude' and 'longitude' in newsApiArguments['location']:
                location = newsApiArguments['location']
                
        newsData = self.newsApiCaller.newsRequest(newsApiArguments['numArticles'], location)

        if newsData != -1:
            for article in newsData:
                self.mqttConnection.publish("news/article", json.dumps(article))

    def foreverLoop(self):
        self.mqttConnection.loop_forever()