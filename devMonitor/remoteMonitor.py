'''
Created on June 30, 2014

@author: tom
'''
import time
from .cancelableThread import CancelableThread
from .configObjects import SerialPort
from .configObjects import Node
from .configObjects import TypedMessage
import pprint

class RemoteMonitor(CancelableThread):
    def __init__(self,config):
        CancelableThread.__init__(self,"RemoteMonitor")
        
        ports = config["serialports"]["list"].split(",")
        for port in ports:  #if list is not empty
            if port != "":
                SerialPort.add(config, port.strip())
                
        nodes = config["nodes"]["list"].split(",")
        for node in nodes:
            if node != "":  #if list is not empty
                Node.add(config,node.strip())
                
        messages = config["messages"]["list"].split(",")
        for msg in messages:
            if msg != "":   #if list is not empty
                TypedMessage.add(config,msg.strip())

    def run(self):
        for port in SerialPort.instances:
            SerialPort.instances[port].doStart()
        while not self.cancelled:
            #TODO rearrange cancel to use a semaphore
            time.sleep(2.0)  #sleep 2 seconds repeatedly until cancelled
        for port in SerialPort.instances:
            SerialPort.instances[port].cancel()
