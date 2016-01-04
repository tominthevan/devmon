'''
Created on June 30, 2014

@author: tom
'''
import time
from .cancelableThread import CancelableThread
#from .configObjects import Server
from queue import Queue, Empty

class EventHandler(CancelableThread):

    eventQ = Queue(maxsize=50)

    def __init__(self,config):
        CancelableThread.__init__(self,"EventHandler")

    @classmethod
    def qEvent(self,ev):
        self.eventQ.put(ev) #this will block until space is available
        #TODO deal with possibility of indefinite wait and lost data
        



    def run(self):
        while not self.cancelled:
            try:
                server,ev = self.eventQ.get(timeout= 2)
            except Empty:
                continue
            server.update(ev)
