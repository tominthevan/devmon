'''
Created on Aug 30, 2013

@author: tom
'''
import urllib.request
import pprint
import string
import time
from ..event import Event
from ..eventHandler import EventHandler


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
        
    def update_(self, ev):
        result = 0
        try:
            req = urllib.request.Request(url=self.URL)
            evDict = Event(*ev).__dict__
            del evDict["time"]
            data = urllib.parse.urlencode(evDict)
            print(data)
            data = data.encode('utf-8')
            f = urllib.request.urlopen(req,data = data)
        except urllib.error.URLError as descr:
            result = descr
        else:
            result = f.read().decode('utf-8').strip("\n ")
            if result == "OK":
                return
        print("Server update error: ")
#       pprint.pprint(sensor_update_dict)
#       print("     Status:",f.status," : ", f.reason)
        print("     Result: ~", result,"~")

