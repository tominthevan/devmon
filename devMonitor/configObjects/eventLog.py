'''
Created on July 26, 2014

EventLog objects store values to be logged by the log handler

@author: tom
'''
import string, os, time, logging
from ..event import Event
from ..logHandler import LogHandler

from .configObject import ConfigObject

class EventLog(ConfigObject):
    instances = {}
    def __init__(self,config,key):
        pass

class NoLogging(EventLog):
    def __init__(self,config,key):
        EventLog.__init__(self,config,key)

    def qEvent(self,evt):
        pass

class CSVFileLog(EventLog):
    def __init__(self,config,key):
        log = config[key]
        self.interval = int(log["interval"])
        roth,rotm = divmod(int(log.get("TODRoll",0)),100)  #rollover time defaults to 0 (midnight)
        self.roTOD = roth * 60 + rotm  # set the time of day of the rollover in minutes
        self.folder = os.path.realpath(os.path.normpath(log["folder"]))
        if not os.path.exists(self.folder):
            self.folder = os.path.normpath(os.getcwd()+"/logfiles")
            if not os.path.exists(self.folder):
                os.mkdir(self.folder)
        self.folder = os.path.normpath(self.folder + "/log")
        self.records = dict()
        EventLog.__init__(self,config,key)

    def qEvent(self,evt):
        LogHandler.qEvent((self,evt))

    def update(self,evt):
        recId = (evt[1],evt[3])     # nodeId,devNo form key
        if recId in self.records:
            dfl,pel = self.records[recId]
        else:
            dfl = DailyFileLog(self.folder, evt, self.roTOD)
            pel = PeriodicEventLog(self.interval, evt)
            self.records[recId] = (dfl,pel)
        while not pel.updated(evt):
            ev = pel.nextLogRec(evt[0])
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

class PeriodicEventLog():
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
            return(True)   #update done

    def nextLogRec(self,time):
            #Get the next log record (in the form of an Event) to emit.
            #Repeated calls will return an event until there is more need to
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
                return(self.ev)

class DailyFileLog():
    SECSPERDAY = 24 * 60 * 60
    def __init__(self, folder, evt, roTOD):
        self.prefix = folder + evt[2] + str(evt[3]) + "-"
        self.fd = None
        self.roTOD = roTOD
        self.roTime = 0

    def update(self, evTime, evStr):
        if evTime >= self.roTime:
            if self.fd != None:
                self.fd.close()
            logging.info(__name__+"log rollover:"+str(evTime)+":"+str(self.roTime))
            evTimeStruc = time.localtime(evTime)    #create an event struct_time for local time
            # a struct_time is a named tuple. Tuples cant be modified so, in order 
            # to modify the struct_time we have to convert it to a list, modify it,
            # and then convert it back to a tuple and then struct_time
            tl = list(evTimeStruc)
            tl[3],tl[4] = divmod(self.roTOD,60)
            tl[5] = 0
            roTimeStruc = time.struct_time(tuple(tl))
            logDay = time.mktime(roTimeStruc)     # the time used to name the daily file
            # check for initial case where the first event recorded is before the rollover
            # time in a day. This can only happen for the first event recorded to a file as
            # the rollover time (self.roTime) is initialized to 0.
            if evTime >= logDay:
                #we are at or past the rollover time for the day 
                self.roTime = logDay + self.SECSPERDAY    # rollover time is 24 hrs after logDay
            else:
                #we are before the rollover time for the day, so we are still recording for the previous day
                self.roTime = logDay

            fname = self.prefix + time.strftime("%Y%m%d",time.localtime(logDay)) + ".csv"
            um = os.umask(0)          # enable read/write by all
            self.fd = open(fname, mode='a')
            um = os.umask(um)         # restore umask
            logging.info(__name__ + ":log file started - " + fname)

        self.fd.write(evStr)
        self.fd.flush()        

