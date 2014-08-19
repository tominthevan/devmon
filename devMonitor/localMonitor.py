'''
localMonitor
    Monitor analog and/or digital devices and report them to one or more 
    www servers - usually a HomeSeer server


Created on Aug 29, 2013

@author: tom
'''
import sched, time
import os.path
import wiringpi2 as wiringpi

from .configObjects import Sensor, Node
from .cancelableThread import CancelableThread
from .event import Event


class LocalMonitor(CancelableThread):

    def __init__(self,config):

        CancelableThread.__init__(self,"LocalMonitor")
        #...process the local sensor part of the log file
        senslist = [item.strip() for item in config["Sensors"]["list"].split(",")]
        self.sensors = []
        for sen in senslist:
            self.sensors.append(Sensor.add(config, sen))


    def run(self):            
        print("Initializing WiringPi2")
        wiringpi.wiringPiSetup()

        localNode = Node.local
        localEvent = Event(0,localNode.id,localNode.devStr,localNode.devNum,[])
        localEvent.values = [0]*len(Sensor.instances)
        lastReport = time.time()
        lastRead = 0.0
        sigChange = False
        while not self.cancelled:
            now = time.time()
            if now - lastRead > localNode.monitorInterval:
                #Read all sensors and schedule their updates and reporting
                lastRead = now
                for key in Sensor.instances:
                    sigChange |= Sensor.instances[key].update()   # read sensor
            if sigChange or (now - lastReport) > localNode.reportInterval:
                for i,sensor in enumerate(self.sensors):
                    localEvent.values[i] = round(sensor.report()*10)
                lastReport = now
                localEvent.time = now
                evt = localEvent.tuple()
                localNode.server.qEvent(evt)
                localNode.eventlog.qEvent(evt)
                sigChange = False
            time.sleep(max(0, min(2,
                                  lastRead + localNode.monitorInterval - now,
                                  lastReport + localNode.reportInterval - now)))
                           
