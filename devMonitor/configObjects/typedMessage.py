'''
Created on July 15, 2014

@author: tom
Process a typed message from a remote node (received by rf12demo):
The message comes as a collection of integers from the SerialPort
    msg[0]  message times stamp
    msg[1]  originating node id
    msg[2:3]node/message type
    msg[4:] dependent on the originating mode
'''

import logging, time
from .configObject import ConfigObject
from .server import Server
from ..event import Event

class TypedMessage(ConfigObject):
    instances = {}
    selector = {}
    def __init__(self,config,key):
        msg = config[key]
        self.id = int(msg["messageid"])
        self.devNum = int(msg["devicenum"])
        TypedMessage.selector[self.id] = self
        self.server = Server.add(config, msg["server"])
        self.lastServerEvent = 0

    @classmethod
    def processMsg(cls, msg, node):
        sel = msg[2]*256 + msg[3]
        if sel in cls.selector:
            cls.selector[sel].processMsg(msg,node)
        else:
            logging.error(__name__ + "Unknown message type:" + str(sel))

                
class TempMonFlexi(TypedMessage):
    def processMsg(self, msg, node):
        #process message from tagged message device
        ev = Event(msg[0], msg[1], node.devStr, node.devNum + self.devNum)
        for i in range(0,int(len(msg)-4),2):
            value = msg[5+i] * 256 + msg[4+i]
            if value >= 32768:
                value -= 65536
            ev.addValue(value)
        evt=ev.tuple()
        now = time.time()
        # don't send the server messages coming too frequently
        # ideally, the node should be set up to emit at the proper interval
        # this is a throttle to prevent server overload in case the node is
        # not well behaved.
        if (now-self.lastServerEvent) > node.minServerEventInterval:
            node.server.qEvent(evt)
            self.lastServerEvent = now
        node.eventlog.qEvent(evt)
                
