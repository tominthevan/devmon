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
            upderr = "URL Error(" + self.URL + "," + descr + ")"
        except http.client.HTTPException as descr:
            upderr = "HTTP Error(" + self.URL + "," + descr + ")"
        except socket.error as descr:
            upderr = "Socket Error(" + self.URL + "," + descr + ")"
        else:
            result = str(f.getcode())
            if result != "200":
                upderr = f.read().decode('utf-8').strip()
        if upderr:
            logging.error(__name__ + ":server update error: " + str(upderr))

