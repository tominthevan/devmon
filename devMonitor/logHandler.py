'''
Created on June 30, 2014

Drives the logging process using the EventLog subclasses determined by
the config file

@author: tom
'''
import time
import pprint
from .event import Event
from .cancelableThread import CancelableThread
from queue import Queue, Empty

class LogHandler(CancelableThread):
    def __init__(self,config):
        CancelableThread.__init__(self,"EventLogger")
        LogHandler.logQ = Queue(maxsize=50)
        
    @classmethod
    def qEvent(self,lev):
        self.logQ.put(lev)#this will block until space is available
        #TODO deal with possibility of indefinite wait and lost data
#        print("log put",self.logQ.qsize(),*lev[1][0:1])

    def run(self):
        while True:
            try:
                lev = LogHandler.logQ.get(timeout= 2)
            except Empty:
                if self.cancelled: return
                continue
            lev[0].update(lev[1])
#            print("log get",self.logQ.qsize(),*lev[1])
