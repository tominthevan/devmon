'''
Created on July 26, 2014

EventLog objects store values to be logged by the log handler

@author: tom
'''
import string, os, time, logging
import time
from ..event import Event
from ..logHandler import LogHandler
from .configObject import ConfigObject

class EventLog(ConfigObject):
    instances = {}
    def __init__(self,config,key):
        pass

    def qEvent(self,evt):
#        print("Not logging:", *evt)
        pass
    def devNum(self,dev,num):
        self.fileNamePrefix = str(dev)+str(num)

class DailyFileLog(EventLog):
    SECSPERDAY = 24 * 60 * 60
    def __init__(self,config,key):
        self.fd = None
        self.nextRollover = 0
        log = config[key]
        roth,rotm = divmod(int(log.get("TODRoll",0)))  #rollover time defaults to 0 (midnight)
        self.roTOD = (roth * 60 + rotm) * 60  # set the time of day of the rollover in second
        curday,cursecs = divmod(time(),self.SECSPERDAY)
        if cursecs < self.roTOD:  # is time before the rollover time of day
            curday -= 1           # if so back up day to previous (for log file naming)
            
        super.__init__(self,config,key)

    def update(self, evTime, evStr):
        if evTime >= self.nextRollover:
            if self.fd != None:
                self.fd.close()
            day,secs = divmod(evTime, self.SECSPERDAY)
            if secs < self.roTOD      # is this a startup and we are before the rollover time of day?
                day = day -1          # if so, back up log day to previous
            day = day * self.SECSPERDAY
            fname = self.fileNamePrefix + time.strftime("%Y%m%d",time.localtime(day)) + ".csv"
            um = os.umask(0)          # enable read/write by all
            self.fd = open(fname, mode='a')
            um = os.umask(um)         # restore ymask
            logging.info(__name__ + ":log file started - " + fname)
            self.nextRollover = day + self.roTOD + self.SECSPERDAY
        self.fd.write(evStr)
        self.fd.flush()
        
class CSVFileLog(DailyFileLog):
    def __init__(self,config,key):
        log = config[key]
        self.interval = int(log["interval"])
        self.folder = os.path.realpath(os.path.normpath(log["folder"]))
        if not os.path.exists(self.folder):
            self.folder = os.path.normpath(os.getcwd()+"/logfiles")
            if not os.path.exists(self.folder):
                os.mkdir(self.folder)
        self.folder = os.path.normpath(self.folder + "/log")
        self.records = dict()
        super.__init__(self,config,key)

    def qEvent(self,evt):
#        print("Logging:", *evt)
        LogHandler.qEvent((self,evt))

    def update(self,evt):
        recId = (evt[1],evt[3])     # nodeId,devNo form key
        if recId in self.records:
            dfl,pea = self.records[recId]
        else:
            dfl = DailyFileLog(self.folder,evt)
            pea = PeriodicEventAccumulator(self.interval, evt)
            self.records[recId] = (dfl,pea)
#        print("updLog1", evt[1], evt[0])
        while not pea.updated(evt):
            ev = pea.nextLogRec(evt[0])
            assert(ev != None)
            dfl.update(ev.time,self.formatCSV(ev))

    def formatCSV(self,ev):
        line = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(ev.time))
        line += ",{0},{1},{2}".format(ev.nodeId,ev.devStr,ev.devNum)
        for val in ev.values: line += ",{0}".format(val)
        return(line + "\n")
    
#############################################
#   Logging Utility Classes
#############################################
#   PeriodicEventAccumulator
#     receive events produced at some rate and accumulate them so they can be recorded at another (longer) interval
#     the recorded event is the average of all events received during the recording interval
class PeriodicEventAccumulator():
    def __init__(self, interval, evt):
        self.ev = Event(*evt)
        self.interval = interval
        self.count = 1
        self.nextRecTime = (int(self.ev.time/self.interval) + 1) * self.interval
#        print("nextrectime",evt[1],self.nextRecTime)

    def updated(self,evt):
        evtime = evt[0]
        assert len(evt[4]) == len(self.ev.values)
        assert evt[1] == self.ev.nodeId and evt[3] == self.ev.devNum
        if evtime >= self.nextRecTime:
            return(False)   #can't update record needs to be emitted first
        else:
            # next record to be written is in the future, just
            # accumulate data
            if self.count == 0:
                # first record of the accumulation interval
                self.ev.values = list(evt[4])
                self.count = 1
            else:
                #sebsequent record of the accumulation interval
                for i,val in enumerate(evt[4]):
                    self.ev.values[i] += val
                self.count += 1
#            print("acc", evt[1], self.count, evt[0])
            return(True)   #update done

    def nextLogRec(self,time):
            #Get the next log record (in the form of an Event) to emit.
            #Repeated calls will return an event until there is no more need to
            #write a record for values accumulated prior to the current event
            #we are trying to log. This may result in more than 1 record to
            #be written until until the event being logged is before time of
            #the next record to be written
            #When there are no more records to be written, None will be returned
            if time < self.nextRecTime:
                return(None)
            else:
                if self.count > 1:
                    #average accumulated values
                    for i in range(len(self.ev.values)):
                        self.ev.values[i] = round(self.ev.values[i]/self.count)
                self.count = 0
                self.ev.time = self.nextRecTime
                self.nextRecTime += self.interval
#                print("Upd nextrectime", self.ev.nodeId, self.nextRecTime)
                return(self.ev)

        

