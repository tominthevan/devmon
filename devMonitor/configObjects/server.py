'''
Created on Aug 30, 2013

@author: tom
'''
import urllib.request
import http.client
import logging
import string
import time
from ..event import Event
from ..eventHandler import EventHandler
import paho.mqtt.client as mqtt

from .configObject import ConfigObject

class Server(ConfigObject):
    instances = {}

    def __init__(self, config, key):
        server = config[key]
        self.update = getattr(self,"update_" + server.get("Updater", ""))
        self.URL = server["URL"]

    def qEvent(self,evTuple):
        EventHandler.qEvent((self,evTuple))

class HSV1(Server):
        
    def update_HS1(self, ev):
        upderr = None
        try:
            req = urllib.request.Request(url=self.URL)
            evDict = Event(*ev).__dict__
            del evDict["time"]
            evdata = urllib.parse.urlencode(evDict)
            logging.debug(__name__ + ": server update: " + evdata)
            evdata = evdata.encode('utf-8')
            f = urllib.request.urlopen(req, data = evdata)
        except urllib.error.URLError as descr:
            upderr = "URL Error(" + self.URL + "," + descr.__str__() + ")"
        except http.client.HTTPException as inst:
            upderr = "HTTP Error(" + self.URL + "," + type(inst) + ")"
        except socket.error as descr:
            upderr = "Socket Error(" + self.URL + "," + descr.__str__() + ")"
        else:
            result = str(f.getcode())
            if result != "200":
                upderr = f.read().decode('utf-8').strip()
        if upderr:
            logging.error(__name__ + ":server update error: " + str(upderr))

class HS3MQTT(Server):

    def __init__(self,config,key):
        super().__init__(config,key)
        server = config[key]
        self.topic = server["Topic"]
        # for now we will not worry about termination modes
        # (us stopping or broker disappearing). In future we could
        # close cleanly on stopping or restart (e.g. if config file
        # is updated). That would require catching an EventHandler
        # cancellation request, performing a disconnect and setting
        # up an MQTT will to notify broker of crashes. Since the broker
        # will be running on the same processor as devMon, even that
        # might not be a reliable means of providing a visual indication
        # devmon is running

        self.mqttc = mqtt.Client()
        self.mqttc.connect(self.URL)
        self.mqttc.loop_start()

    def update_HS3(self,evt):
        #format and publish the values in the event individually
        ev = Event(*evt)
        topicStart = self.topic + ev.devStr
        item = ev.devNum
        for value in ev:
            self.mqttc.publish(topicStart + str(item), payload = str(value))
            logging.debug(__name__ + "HS3 update for:" + topicStart + str(item)+ "=" + str(value))
            item = item + 1
        
