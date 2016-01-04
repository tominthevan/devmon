'''
Created on July 15, 2014

@author: tom
'''
import time

class Event(object):
    def __init__(self,when,nodeId,devStr,devNum,value=[]):
        self.time = when
        self.nodeId = nodeId
        self.devStr = devStr
        self.devNum = devNum
        try:
            self.values = list(value)
        except TypeError:
            self.values = [value]

    def addValue(self,value):
        self.values.append(value)

    def __iter__(self):
        for item in self.values:
            yield(item)

    def tuple(self):
        return (self.time,self.nodeId,self.devStr,self.devNum,tuple(self.values))

        
