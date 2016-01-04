'''
Created on July 7, 2014

@author: tom
'''
from threading import Thread
import logging

class CancelableThread(Thread):
    def __init__(self, name):
        Thread.__init__(self, name = name)
        self.cancelled = True

    def cancel(self):
        if not self.cancelled:
            self.cancelled = True
            tries = 0
            while tries < 10 and self.is_alive():
                # cancel() is called by the parent thread.
                # self used below refers to the thread 
                # being cancelled and not the parent thread
                self.join(timeout = 2.0)
                tries = tries + 1
            if tries >= 10:
                logging.error(__name__+":cancel failed for: "+self.name)

    def isCancelled(self):
        return(self.cancelled)

    def doStart(self):
        self.cancelled = False
        self.start()

    def run(self):
        self.cancelled = True

