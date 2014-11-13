'''
Created on June 30, 2014

@author: tom
'''
import time, serial, logging
from ..cancelableThread import CancelableThread
from .node import Node
from queue import Queue
from .configObject import ConfigObject

class SerialPort(ConfigObject,CancelableThread):
    instances = {}
    
    def __init__(self,config,key):
        CancelableThread.__init__(self,"Port:"+key)
        port = config[key]
        self.dev = port["serialdevice"]
        self.baudrate = int(port["serialbaudrate"])
        self.stopbits = float(port["serialstopbits"])
        self.parity = port["serialparity"].upper()
        self.signature = port["signature"]
        self.synced = False
        self.cancelled = False

    def getLine(self,ser):
        if self.cancelled:
            return b"\n"
        return ser.readline()
        
    def openSerial(self):
        self.synced = False
        try:
            ser = serial.Serial(port = self.dev,
                            baudrate = self.baudrate,
                            bytesize = 8,
                            parity = self.parity,
                            stopbits = self.stopbits,
                            timeout = 2,
                            interCharTimeout = 0.5)
        except serial.SerialException:
            logging.error("Serial Port open error")
            ser = None
            self.cancelled = True
        return ser
            

    def run(self):
        ser = self.openSerial()
        while not self.cancelled:
            if self.synced:
                self.processMsg(self.getLine(ser))
            else:
                self.synced = self.initRemote(ser)

    def processMsg(self, msg):
        logging.debug("Unexpected call to SerialPort.processMsg")

    def initRemote(self, ser):
        logging.debug("unexpected call to SerialPort.initRemote")

class Rf12demoPort(SerialPort):

    def processMsg(self,msg):
        #reassemble message from rf12emo
        # format is:
        # OK ii nn mm ss ss ss ...
        # where:
        #   OK is "OK"
        #   the remainder of each message is a sequence of small integers followed by linefeed
        #   ii is originiting node ID (1..30)
        #   nn is the originating node type (0..256)
        #   mm is the node message id (0..256)
        #   ss is a sequence of one or more byte values (0..256)
        msgparts = msg.decode("utf-8").split()
        if len(msgparts) > 0 and msgparts[0] == "OK":
            msgparts[0] = time.time()
            for p in range(1,len(msgparts)):
                #TODO handle crap in message
                msgparts[p] = int(msgparts[p])
#            print(self.synced, msgparts)
            Node.processMsg(msgparts)

    def initRemote(self, ser):
        # initialize a jeeNode running rf12demo sketch
        ser.flushInput()
        #force a reset
        ser.setDTR(True)
        ser.setDTR(False)
        ser.setDTR(True)
        if len(self.signature) == 0:
            return True
        #forcing a reset should cause the sketch to send a string identifying itself
        for i in range(5):        
            line = self.getLine(ser).decode('utf-8')
            if len(line) >= len(self.signature) and self.signature == line[:len(self.signature)]:
                return True #if we get the expected signature string
        return False        #if no signature found     
