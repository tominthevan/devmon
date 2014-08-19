'''
Created on June 30, 2014

@author: tom
'''
import time
import pprint
from .event import Event
from .cancelableThread import CancelableThread
from queue import Queue, Empty

class EventLogger(CancelableThread):
    def __init__(self,config):
        CancelableThread.__init__(self,"EventLogger")
        self.logQ = Queue(maxsize=50)
        
    @classmethod
    def eventLog(self,ev):
        self.logQ.put(ev)#this will block until space is available
        #TODO deal with possibility of indefinite wait and lost data

    def run(self):
        while not self.cancelled:
            try:
                ev = self.logQ.get(timeout= 2)
            except Empty:
                continue
            self.updateLog(ev)

    def updateLog(self,ev):
        event = Event(*ev)
        pprint.pprint("Logging:",event)
            
