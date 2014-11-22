'''
Created on July 15, 2014

@author: tom
Direct the message processing from a remote node (received by rf12demo):
The message comes as a collection of integers from the SerialPort
    msg[0] message times stamp
    msg[1] originating node id
    msg[2:] dependent on the originating mode
'''

from .configObject import ConfigObject
from .server import Server
from .typedMessage import TypedMessage
from .eventLog import EventLog

class Node(ConfigObject):
    instances = {}
    selector = {}
    def __init__(self,config,key):
        node = config[key]
        self.server = Server.add(config, node["server"])
        self.id = int(node["nodeid"])
        if self.id in Node.selector:
            #TODO Handle duplicate use of nodeId
            pass
        else:
            Node.selector[self.id] = self
        self.devStr = node["devicestr"]
        self.devNum = int(node["devicenum"])
        log = node.get("eventlog", None)
        if log != None:
            log = EventLog.add(config,log)
        else:   # EventLog base class provides the default "no logging" service
            log = EventLog
        self.eventlog = log

    @classmethod
    def processMsg(cls, msg):
        id = msg[1]
        if id in cls.selector:
            cls.selector[id].processMsg(msg)
        else:
            #TODO handle error
            pass
        
        
class MultiMsgNode(Node):

    def processMsg(self, msg):
        #process message from typed message device
        TypedMessage.processMsg(msg, self)

        
# create special local node for reporting all sensors connected to Raspberry Pi
class RaspberryPi(Node):
    def __init__(self,config,key):
        Node.__init__(self,config,key)
        node = config[key]
        self.devNum = int(node["devicenum"])
        self.devStr = node["devicestr"]
        self.monitorInterval = float(node["MonitorInterval"])
        self.reportDelta = float(node["ReportDelta"])
        self.reportInterval = float(node["ReportInterval"])
        Node.local = self

                
