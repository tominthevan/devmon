'''
Created on Aug 30, 2013

@author: tom
'''
from .configObject import ConfigObject
from .device import Device
from .interface import Interface
from .server import Server
from ..event import Event
from .node import Node

import sched
import time, random, logging

class Sensor(ConfigObject):
    instances = {}
    
    def __init__(self, config, key):
        sen = config[key]
        self.name = key
        self.device = Device.add(config, sen["Device"])
        self.interface = Interface.add(config,sen["Interface"])
        self.channel = self.interface.channel(sen["channel"])
        self.value = None
        self.reportedValue = 0.0
        
    def update(self):
        try:
            # read the current sensor value and report it if reporting criteria are met
            # retreive the sensor's current raw value
            rawvalue = self.interface.get_value(self.channel)
            # convert the raw value to appropriate units
            # and blend (i.e. smooth) it with the current (70% history, 30% new)
            value = self.device.convert(rawvalue)
            if self.value == None:
                self.value = value
            else:
                self.value = self.value * 0.7 + value * 0.3
            # determine if significant change
            return abs(value - self.reportedValue) >= Node.local.reportDelta
        except Exception as excpt:
            logging.error("Cant'read from " + self.name + " - " +
                          self.interface.__class__.__name__ + "|" +
                          self.device.__class__.__name__ + "|" +
                          self.channel + ":" + str(excpt))
            return False

        # report the sensor
    def report(self):
        self.reportedValue = self.value
        return self.value

